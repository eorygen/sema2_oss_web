import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save, pre_save
from jsonfield import JSONField
from push_notifications.models import APNSDevice, GCMDevice
from uuidfield import UUIDField
from sema2.managers import AnswerSetUniqueManager


# -----------------------------------------------------------------------------
#  Program
# -----------------------------------------------------------------------------


class Program(models.Model):

    EXPORT_STATUS_READY = 0
    EXPORT_STATUS_IN_PROGRESS = 1
    EXPORT_STATUS_ERROR = 2
    EXPORT_STATUS_COMPLETED_OK = 3

    EXPORT_STATUS_CHOICES = (
        (EXPORT_STATUS_READY, "Ready"),
        (EXPORT_STATUS_IN_PROGRESS, "In Progress"),
        (EXPORT_STATUS_ERROR, "Error"),
        (EXPORT_STATUS_COMPLETED_OK, "Success")
    )

    PROGRAM_STATUS_ACTIVE = 0
    PROGRAM_STATUS_ARCHIVED = 1

    PROGRAM_STATUS_CHOICES = (
        (PROGRAM_STATUS_ACTIVE, "Active"),
        (PROGRAM_STATUS_ARCHIVED, "Archived"),
    )

    status = models.IntegerField(default=PROGRAM_STATUS_ACTIVE, choices=PROGRAM_STATUS_CHOICES)

    is_enabled = models.BooleanField(default=False)

    feature_enable_conditional_question_sets = models.BooleanField(default=False)

    active_version = models.OneToOneField('ProgramVersion', null=True, blank=True, related_name='parent')
    editing_version = models.OneToOneField('ProgramVersion', null=True, blank=True, related_name='editing_parent')
    admins = models.ManyToManyField(User, related_name='administered_programs')
    participants = models.ManyToManyField(User, related_name='participated_programs', through='ProgramParticipantBridge')

    contact_name = models.CharField(max_length=120)
    contact_email = models.CharField(max_length=120)
    contact_phone_number = models.CharField(max_length=60)

    export_status = models.IntegerField(default=EXPORT_STATUS_READY, choices=EXPORT_STATUS_CHOICES)
    export_completion_timestamp = models.DateTimeField(null=True, blank=True)
    export_initiator_user = models.ForeignKey(User, blank=True, null=True)
    export_percentage = models.IntegerField(default=0)

    cached_compliance_fraction = models.FloatField(default=0)
    cached_top_compliance_participant_id_list = JSONField(blank=True, null=True)
    cached_longest_sync_interval_participant_id_list = JSONField(blank=True, null=True)

    def __unicode__(self):
        if self.editing_version is None:
            return "Invalid Program - Please add a program version"
        else:
            return str(self.editing_version)

    def clone(self):

        # This will create a new program and a new bunch of other stuff
        new_program = Program.objects.create(
            is_enabled=True,
            contact_name=self.contact_name,
            contact_email=self.contact_email,
            contact_phone_number=self.contact_phone_number
        )

        # Now copy the admins and participants
        for admin in self.admins.all():
            new_program.admins.add(admin)

        for participant in self.participants.all():

            try:
                existing = ProgramParticipantBridge.objects.get(user=participant, program=self)

                ProgramParticipantBridge.objects.create(
                    user=participant,
                    program=new_program,
                    device_push_token=existing.device_push_token,
                    program_participant_status=ProgramParticipantBridge.PROGRAM_PARTICIPANT_STATUS_DISABLED,
                    timezone=existing.timezone,
                    force_data_update=True,
                    app_version_string=existing.app_version_string,
                    app_version_number=existing.app_version_number,
                    app_platform_name=existing.app_platform_name,
                    is_running_latest_app_version=existing.is_running_latest_app_version
                )

            except ProgramParticipantBridge.DoesNotExist:
                ProgramParticipantBridge.objects.create(
                    user=participant,
                    program=new_program
                )

        new_editing_version = new_program.editing_version

        if self.active_version:
            source_version = self.active_version
        else:
            source_version = self.editing_version

        new_editing_version.display_name = source_version.display_name
        new_editing_version.description = source_version.description

        new_editing_version.display_name += " (Copy)"

        # Delete data created after saving the Program
        new_editing_version.question_sets.all().delete()
        new_editing_version.surveys.all().delete()
        new_editing_version.schedules.all().delete()

        # Clone Schedules
        for schedule in source_version.schedules.all():
            schedule.pk = None
            schedule.program_version = new_editing_version
            schedule.save()

        # Clone Question Sets
        for question_set in source_version.question_sets.filter(status=QuestionSet.QUESTION_SET_STATUS_ACTIVE):
            new_set = QuestionSet.clone(question_set, new_editing_version)

        # Now we have cloned all of the question sets we need to re-link all of the conditional QS predicates to the latest versions of the question sets.
        predicates = ConditionalQuestionSetPredicate.objects.filter(question__set__program_version=new_editing_version)

        for predicate in predicates:
            target_question_set = QuestionSet.objects.get(uuid=predicate.target_question_set, program_version=new_editing_version)
            predicate.target_question_set = target_question_set
            predicate.save()

        # Clone Surveys
        for survey in source_version.surveys.all():
            new = Survey.clone(survey, new_editing_version)

        new_editing_version.save()
        new_editing_version.editing_status = ProgramVersion.EDITING_STATUS_PUBLISHED
        new_program.active_version = new_editing_version
        new_program.save()

    def create_new_version(self):

        if not self.is_locked():
            raise Exception("You are already in editing mode")

        active_version = self.active_version
        new_revision_number = active_version.revision_number+1

        # What is the current highest revision number
        latest_revision_number = self.versions.all().aggregate(Max('revision_number'))["revision_number__max"]

        new_version = ProgramVersion.objects.create(
            program=self,
            revision_number=new_revision_number,
            display_name=active_version.display_name,
            description=active_version.description
        )

        # Clone Schedules
        for schedule in active_version.schedules.all():
            schedule.pk = None
            schedule.program_version = new_version
            schedule.save()

        # Clone Question Sets
        for question_set in active_version.question_sets.filter(status=QuestionSet.QUESTION_SET_STATUS_ACTIVE):
            new_set = QuestionSet.clone(question_set, new_version)

        # Now we have cloned all of the question sets we need to re-link all of the conditional QS predicates to the latest versions of the question sets.
        predicates = ConditionalQuestionSetPredicate.objects.filter(question__set__program_version=new_version)
        invalid_predicate_ids = []

        for predicate in predicates:

            try:
                target_question_set = QuestionSet.objects.get(uuid=predicate.target_question_set.uuid, program_version=new_version)

                predicate.target_question_set = target_question_set
                predicate.save()
            except QuestionSet.DoesNotExist:
                invalid_predicate_ids.append(predicate.id)

        ConditionalQuestionSetPredicate.objects.filter(pk__in=invalid_predicate_ids).delete()

        # Clone Surveys
        for survey in active_version.surveys.all():
            new = Survey.clone(survey, new_version)

        self.editing_version = new_version
        self.save()

    def is_locked(self):
        return not self.editing_version or self.editing_version.editing_status == ProgramVersion.EDITING_STATUS_PUBLISHED


class ProgramVersion(models.Model):

    EDITING_STATUS_DRAFT = 0
    EDITING_STATUS_PUBLISHED = 1

    EDITING_STATUS_CHOICES = (
        (EDITING_STATUS_DRAFT, "Draft"),
        (EDITING_STATUS_PUBLISHED, "Published"),
    )

    editing_status = models.IntegerField(default=EDITING_STATUS_DRAFT, choices=EDITING_STATUS_CHOICES)
    program = models.ForeignKey(Program, related_name='versions')
    display_name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)
    revision_number = models.IntegerField()

    def __unicode__(self):
        return '{} (v{})'.format(self.display_name, self.revision_number)


class ProgramParticipantBridge(models.Model):

    PROGRAM_PARTICIPANT_STATUS_ACTIVE = 0
    PROGRAM_PARTICIPANT_STATUS_DISABLED = 1
    PROGRAM_PARTICIPANT_STATUS_ARCHIVED = 2

    PROGRAM_PARTICIPANT_CHOICES = (
        (PROGRAM_PARTICIPANT_STATUS_ACTIVE, "Active"),
        (PROGRAM_PARTICIPANT_STATUS_DISABLED, "Stopped"),
        (PROGRAM_PARTICIPANT_STATUS_ARCHIVED, "Archived"),
    )

    user = models.ForeignKey(User, related_name='program_profiles')
    program = models.ForeignKey(Program, related_name='program_profiles')

    program_participant_status = models.IntegerField(default=PROGRAM_PARTICIPANT_STATUS_ACTIVE, choices=PROGRAM_PARTICIPANT_CHOICES)

    custom_start_hour = models.IntegerField(default=9)
    custom_start_minute = models.IntegerField(default=0)

    custom_stop_hour = models.IntegerField(default=17)
    custom_stop_minute = models.IntegerField(default=0)

    use_custom_start_stop_time = models.BooleanField(default=False)

    force_data_update = models.BooleanField(default=False)

    cached_received_answer_set_count = models.IntegerField(default=0)
    cached_answered_answer_set_count = models.IntegerField(default=0)
    cached_compliance_fraction = models.FloatField(default=0)
    cached_last_upload_timestamp = models.DateTimeField(blank=True, null=True)
    cached_last_sync_timestamp = models.DateTimeField(blank=True, null=True)
    cached_last_sync_interval_seconds = models.IntegerField(default=-1)

    device_push_token = models.TextField(blank=True, null=True)
    app_id = models.CharField(max_length=60, default=settings.DEFAULT_IOS_APP_ID)
    app_version_string = models.CharField(max_length=20, default="1.0.0")
    app_version_number = models.IntegerField(default=1)
    is_running_latest_app_version = models.BooleanField(default=False)

    app_platform_name = models.CharField(max_length=10, default='unknown')

    timezone = models.CharField(max_length=40, blank=True, null=True)

    compliance_start_timestamp = models.DateTimeField(blank=True, null=True)

    def get_device(self):

        if self.app_platform_name == 'ios':

            try:
                device = APNSDevice.objects.filter(registration_id=self.device_push_token).first()
                if device is None:
                    device = APNSDevice.objects.create(registration_id=self.device_push_token, name=str(self.user.username))

            except APNSDevice.DoesNotExist:
                device = APNSDevice.objects.create(registration_id=self.device_push_token, name=str(self.user.username))

        elif self.app_platform_name == 'android':

            try:
                device = GCMDevice.objects.filter(registration_id=self.device_push_token).first()
                if device is None:
                    device = GCMDevice.objects.create(registration_id=self.device_push_token, name=str(self.user.username))
            except GCMDevice.DoesNotExist:
                device = GCMDevice.objects.create(registration_id=self.device_push_token, name=str(self.user.username))

        return device

    def send_content_update_message(self):

        if self.device_push_token is not None and self.device_push_token is not '<invalid>':

            try:
                device = self.get_device()

                extra = {
                    "type": "content_update",
                    "program_id": self.program.pk
                }

                from django.conf import settings

                if self.app_platform_name == 'ios':
                    certfile = settings.PUSH_NOTIFICATION_APP_ID_TO_CERT_MAPPING[self.app_id]
                    device.send_message(None, extra=extra, content_available=True, certfile=certfile)
                else:
                    device.send_message(None, extra=extra)

            except Exception, e:
                pass


class Schedule(models.Model):

    program_version = models.ForeignKey(ProgramVersion, related_name='schedules')
    uuid = UUIDField()

    display_name = models.CharField(max_length=60)

    interval_minutes = models.IntegerField(default=120)
    expiry_minutes = models.IntegerField(default=120)
    start_time_hours = models.IntegerField(default=9)
    start_time_minutes = models.IntegerField(default=0)
    stop_time_hours = models.IntegerField(default=17)
    stop_time_minutes = models.IntegerField(default=0)
    offset_plus_minus_minutes = models.IntegerField(default=0)

    allow_monday = models.BooleanField(default=True)
    allow_tuesday = models.BooleanField(default=True)
    allow_wednesday = models.BooleanField(default=True)
    allow_thursday = models.BooleanField(default=True)
    allow_friday = models.BooleanField(default=True)
    allow_saturday = models.BooleanField(default=True)
    allow_sunday = models.BooleanField(default=True)

    def __unicode__(self):
        return '{} - {}'.format(self.program_version, self.uuid)

    class Meta:
        ordering = ['id']


class EventLog(models.Model):

    LOG_NOTE = 0

    LOG_APP_SYNC = 1
    LOG_APP_DATA_UPLOAD = 2
    LOG_APP_UPGRADE = 3

    LOG_PROGRAM_EDIT = 4
    LOG_PROGRAM_PUBLISH = 5
    LOG_PROGRAM_DATA_EXPORT = 6

    LOG_USER_STATE_CHANGE = 7

    LOG_CHOICES = (
        (LOG_NOTE, "Note"),
        (LOG_APP_SYNC, "Sync"),
        (LOG_APP_DATA_UPLOAD, "Data Upload"),
        (LOG_APP_UPGRADE, "App Upgrade"),
        (LOG_PROGRAM_EDIT, "Program Edit"),
        (LOG_PROGRAM_PUBLISH, "Program Publish"),
        (LOG_PROGRAM_DATA_EXPORT, "Data Export"),
        (LOG_USER_STATE_CHANGE, "User State Change"),
    )

    log_type = models.IntegerField(default=LOG_NOTE, choices=LOG_CHOICES)
    program_version = models.ForeignKey(ProgramVersion, related_name='events')
    user = models.ForeignKey(User, related_name='events', blank=True, null=True)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = JSONField(blank=True, null=True)

    def __unicode__(self):
        return self.get_log_type_display()

    @classmethod
    def log_sync_event_for_user(cls, program, user, had_existing_data, did_update):

        log = EventLog.objects.create(
            user=user,
            log_type=EventLog.LOG_APP_SYNC,
            program_version=program.active_version,
            description='Synchronised with server',
            data={'did_update': did_update, 'had_existing_data': had_existing_data}
        )

    @classmethod
    def log_upload_event_for_user(cls, program, user):

        log = EventLog.objects.create(
            user=user,
            log_type=EventLog.LOG_APP_DATA_UPLOAD,
            program_version=program.active_version,
            description='Uploaded answers'
        )

    @classmethod
    def log_program_unlocked_event(cls, program, user):

        log = EventLog.objects.create(
            user=user,
            log_type=EventLog.LOG_PROGRAM_EDIT,
            program_version=program.active_version,
            description="User '{}' unlocked program '{}'".format(user.email, program.editing_version.display_name)
        )

    @classmethod
    def log_program_published_event(cls, program, user):

        log = EventLog.objects.create(
            user=user,
            log_type=EventLog.LOG_PROGRAM_PUBLISH,
            program_version=program.active_version,
            description="User '{}' published program '{}'".format(user.email, program.editing_version.display_name)
        )

    class Meta:
        ordering = ['id']

# -----------------------------------------------------------------------------
#  Questions
# -----------------------------------------------------------------------------


class Survey(models.Model):

    TRIGGER_MODE_SCHEDULED = 0
    TRIGGER_MODE_ADHOC = 1

    TRIGGER_MODE_CHOICES = (
        (TRIGGER_MODE_SCHEDULED, "Scheduled"),
        (TRIGGER_MODE_ADHOC, "Adhoc"),
    )

    SURVEY_STATUS_ACTIVE = 0
    SURVEY_STATUS_ARCHIVED = 1

    SURVEY_STATUS_CHOICES = (
        (SURVEY_STATUS_ACTIVE, "Active"),
        (SURVEY_STATUS_ARCHIVED, "Archived"),
    )

    status = models.IntegerField(default=SURVEY_STATUS_ACTIVE, choices=SURVEY_STATUS_CHOICES)

    program_version = models.ForeignKey(ProgramVersion, related_name='surveys')
    participants = models.ManyToManyField(User, related_name='surveys')

    schedule = models.ForeignKey(Schedule, related_name='surveys', null=True, blank=True)

    display_name = models.TextField()
    randomise_set_order = models.BooleanField(default=False)
    trigger_mode = models.IntegerField(default=TRIGGER_MODE_SCHEDULED, choices=TRIGGER_MODE_CHOICES)
    max_iterations = models.IntegerField(default=-1)
    uuid = UUIDField()

    class Meta:
        ordering = ['id']

    @classmethod
    def clone(cls, survey, program_version):

        if survey.schedule:
            new_schedule = Schedule.objects.get(uuid=survey.schedule.uuid, program_version=program_version)
        else:
            new_schedule = None

        new = Survey.objects.create(
            program_version=program_version,
            uuid=survey.uuid,
            display_name=survey.display_name,
            randomise_set_order=survey.randomise_set_order,
            trigger_mode=survey.trigger_mode,
            max_iterations=survey.max_iterations,
            schedule=new_schedule,
            status=survey.status
        )

        # For each person assigned to this survey
        for user in survey.participants.all():
            # Add the user to the new survey
            new.participants.add(user)

        # Copy over the question sets
        for question_set in survey.question_sets.filter(status=QuestionSet.QUESTION_SET_STATUS_ACTIVE):
            new_question_set = QuestionSet.objects.get(uuid=question_set.uuid, program_version=program_version)
            new.question_sets.add(new_question_set)
            new.save()

        return new


class QuestionSet(models.Model):

    QUESTION_SET_STATUS_ACTIVE = 0
    QUESTION_SET_STATUS_ARCHIVED = 1

    QUESTION_SET_STATUS_CHOICES = (
        (QUESTION_SET_STATUS_ACTIVE, "Active"),
        (QUESTION_SET_STATUS_ARCHIVED, "Archived"),
    )

    status = models.IntegerField(default=QUESTION_SET_STATUS_ACTIVE, choices=QUESTION_SET_STATUS_CHOICES)

    display_name = models.CharField(max_length=60)
    group = models.ManyToManyField(Survey, related_name='question_sets', blank=True)
    program_version = models.ForeignKey(ProgramVersion, related_name='question_sets')
    randomise_question_order = models.BooleanField(default=False)
    uuid = UUIDField()

    class Meta:
        ordering = ['id']

    @classmethod
    def clone(cls, other_set, new_version):

        new_set = QuestionSet.objects.create(
            program_version=new_version,
            display_name=other_set.display_name,
            randomise_question_order=other_set.randomise_question_order,
            uuid=other_set.uuid,
            status=other_set.status
        )

        for question in other_set.questions.all():

            new_question = Question.objects.create(
                set=new_set,
                uuid=question.uuid,
                randomise_option_order=question.randomise_option_order,
                question_type=question.question_type,
                question_text=question.question_text,
                question_tag=question.question_tag,
                min_value=question.min_value,
                min_label=question.min_label,
                max_value=question.max_value,
                max_label=question.max_label
            )

            for option in question.options.all():

                new_option = QuestionOption.objects.create(
                    question=new_question,
                    label=option.label,
                    value=option.value
                )

            for predicate in question.predicates.all():

                new_predicate = ConditionalQuestionSetPredicate.objects.create(
                    question=new_question,
                    action=predicate.action,
                    enabled=predicate.enabled,
                    target_question_set=predicate.target_question_set,
                    target_value=predicate.target_value,
                    target_min_value_incl=predicate.target_min_value_incl,
                    target_max_value_incl=predicate.target_max_value_incl
                )

        return new_set


class Question(models.Model):

    QUESTION_TYPE_TEXT = 0
    QUESTION_TYPE_MULTICHOICE = 1
    QUESTION_TYPE_RADIO = 2
    QUESTION_TYPE_SLIDER = 3

    QUESTION_TYPE_CHOICES = (
        (QUESTION_TYPE_TEXT, "Text"),
        (QUESTION_TYPE_MULTICHOICE, "Mutichoice"),
        (QUESTION_TYPE_RADIO, "Radio"),
        (QUESTION_TYPE_SLIDER, "Slider"),
    )

    set = models.ForeignKey(QuestionSet, related_name='questions')
    uuid = UUIDField()

    randomise_option_order = models.BooleanField(default=False)

    question_type = models.IntegerField(default=QUESTION_TYPE_TEXT, choices=QUESTION_TYPE_CHOICES)
    question_text = models.TextField()
    question_tag = models.CharField(max_length=60)

    min_value = models.IntegerField(default=1)
    min_label = models.CharField(max_length=255, default="Min")

    max_value = models.IntegerField(default=5)
    max_label = models.CharField(max_length=255, default="Max")

    class Meta:
        ordering = ['id']


class QuestionOption(models.Model):

    question = models.ForeignKey(Question, related_name='options')

    label = models.CharField(max_length=255)
    value = models.IntegerField(default=-1)

    class Meta:
        ordering = ['id']


class ConditionalQuestionSetPredicate(models.Model):

    PREDICATE_ACTION_JUMP = 0

    action = models.IntegerField(default=PREDICATE_ACTION_JUMP)

    question = models.ForeignKey(Question, related_name='predicates')

    enabled = models.BooleanField(default=True)

    target_question_set = models.ForeignKey(QuestionSet, related_name='predicates', blank=True, null=True)

    target_value = models.TextField(null=True, blank=True)
    target_option = models.ForeignKey(QuestionOption, blank=True, null=True)

    target_min_value_incl = models.IntegerField(default=-1)
    target_max_value_incl = models.IntegerField(default=-1)

    def link_to_option_if_unlinked(self):
        if self.target_option is None:
            self.link_to_option()
            self.save()

    def link_to_option(self):
        if self.target_value is not None and self.target_value is not '':
            if self.question.question_type in [Question.QUESTION_TYPE_MULTICHOICE, Question.QUESTION_TYPE_RADIO]:
                self.target_option = self.question.options.get(value=int(self.target_value))

    def get_desc(self):

        if self.target_question_set is None:
            return "No target question set selected."

        if self.question.question_type in [Question.QUESTION_TYPE_MULTICHOICE, Question.QUESTION_TYPE_RADIO]:
            if self.target_option:
                return "Jump to '{}' when answer is '{}'".format(self.target_question_set.display_name, self.target_option.label)
            else:
                return "Jump to '{}' when answer is '{}'".format(self.target_question_set.display_name, self.target_value)
        elif self.question.question_type == Question.QUESTION_TYPE_TEXT:
            return "Jump to '{}' when answer contains '{}'".format(self.target_question_set.display_name, self.target_value)
        else:
            return "Jump to '{}' when answer is between '{}' and '{}' (inclusive)".format(self.target_question_set.display_name, self.target_min_value_incl, self.target_max_value_incl)

    def get_conditional_desc(self):

        if self.question.question_type in [Question.QUESTION_TYPE_MULTICHOICE, Question.QUESTION_TYPE_RADIO]:
            if self.target_option:
                return "{} = {}".format(self.question.question_tag, self.target_option.label)
            else:
                return "{} = {}".format(self.question.question_tag, self.target_value)
        elif self.question.question_type == Question.QUESTION_TYPE_TEXT:
            return "{} contains {}".format(self.question.question_tag, self.target_value)
        else:
            return "{} is {} <=> {} (inclusive)".format(self.question.question_tag, self.target_min_value_incl, self.target_max_value_incl)

    class Meta:
        ordering = ['id']

# -----------------------------------------------------------------------------
#  Answer
# -----------------------------------------------------------------------------


class AnswerSet(models.Model):

    user = models.ForeignKey(User, related_name='answer_sets', on_delete=models.SET_NULL, null=True, blank=True)
    program_version = models.ForeignKey(ProgramVersion, related_name='answer_sets', on_delete=models.SET_NULL, null=True, blank=True)
    uuid = UUIDField()

    objects = models.Manager()  # The default manager.
    unique_objects = AnswerSetUniqueManager()

    survey = models.ForeignKey(Survey, related_name='answer_sets', on_delete=models.SET_NULL, null=True, blank=True)
    iteration = models.IntegerField()

    created_timestamp = models.DateTimeField()
    delivery_timestamp = models.DateTimeField()
    expiry_timestamp = models.DateTimeField()
    completed_timestamp = models.DateTimeField(blank=True, null=True)
    uploaded_timestamp = models.DateTimeField(auto_now_add=True)

    timezone = models.CharField(max_length=40, blank=True, null=True)

    is_duplicate = models.BooleanField(default=False)

    def __unicode__(self):
        return 'SUR: {} - PK: {} - IT: {} - {} - UUID: {}'.format(self.survey, self.pk, self.iteration, self.uploaded_timestamp, self.uuid)

    @property
    def has_answers(self):
        return self.answers.count() > 0


class Answer(models.Model):
    set = models.ForeignKey(AnswerSet, related_name='answers')
    question = models.ForeignKey(Question, related_name='answer', on_delete=models.SET_NULL, null=True, blank=True)

    answer_value = models.TextField()
    answered_option = models.ForeignKey(QuestionOption, blank=True, null=True)

    answered_timestamp = models.DateTimeField()
    displayed_timestamp = models.DateTimeField()

    reaction_time_ms = models.IntegerField(default=0)

    def __unicode__(self):
        return '{} - {}'.format(self.set, self.answer_value)

    def link_to_option(self):

        if self.answered_option is None and self.question.question_type in (Question.QUESTION_TYPE_MULTICHOICE, Question.QUESTION_TYPE_RADIO):

            try:
                option = QuestionOption.objects.get(pk=int(self.answer_value))
                self.answered_option = option
                self.save()
            except QuestionOption.DoesNotExist, e:
                print "Cannot find matching option for answer value {}->{}".format(self.pk, self.answer_value)


class ProgramInvite(models.Model):

    INVITE_TYPE_PARTICIPANT = 0
    INVITE_TYPE_TEAM = 1

    inviting_user = models.ForeignKey(User, related_name='invitations')
    invitation_type = models.IntegerField(default=INVITE_TYPE_PARTICIPANT)
    program = models.ForeignKey(Program, related_name='invitations')

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    welcome_message = models.TextField(default="", blank=True)

    is_existing_user = models.BooleanField(default=False)

    require_email_confirmation = models.BooleanField(default=False)
    has_been_confirmed = models.BooleanField(default=False)

    username = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)

    sent_timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{} {}".format(self.first_name, self.last_name)


class ProgramParticipantState(models.Model):

    user = models.ForeignKey(User, related_name='participant_states')
    survey_uuid = models.UUIDField()
    current_iteration = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '{} (v{})'.format(self.user, self.survey_uuid, self.current_iteration)

    @classmethod
    def get_for_user_and_survey_uuid(self, user, survey_uuid):

        try:
            state = ProgramParticipantState.objects.get(user=user, survey_uuid=survey_uuid)
        except ProgramParticipantState.DoesNotExist:
            state = ProgramParticipantState.objects.create(user=user, survey_uuid=survey_uuid)

        return state


from signal_processor import process_program_save, process_participant_invite_save, process_answer_set_save, process_answer_set_pre_save, \
    process_conditional_question_set

post_save.connect(process_program_save, sender=Program, dispatch_uid="process_program_save")
post_save.connect(process_participant_invite_save, sender=ProgramInvite, dispatch_uid="process_participant_invite_save")
post_save.connect(process_answer_set_pre_save, sender=AnswerSet, dispatch_uid="process_answer_set_pre_save")
post_save.connect(process_answer_set_save, sender=AnswerSet, dispatch_uid="process_answer_set_save")
pre_save.connect(process_conditional_question_set, sender=ConditionalQuestionSetPredicate, dispatch_uid="process_conditional_question_set_save")
