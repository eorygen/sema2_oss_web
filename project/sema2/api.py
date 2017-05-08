import json
import random
import uuid
from allauth.account.forms import ResetPasswordForm
import arrow
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import FieldError, FieldDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.decorators import detail_route, list_route
from rest_framework.fields import IntegerField
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.serializers import ModelSerializer

from boosted_uplink.models import AppUpdateConfig
from sema2 import tasks
from sema2.models import Program, ProgramVersion, ProgramParticipantState, Schedule, EventLog, \
    Survey, QuestionSet, AnswerSet, Answer, Question, QuestionOption, ProgramInvite, ProgramParticipantBridge, \
    ConditionalQuestionSetPredicate


# -----------------------------------------------------------------------------
#  Serializers
# -----------------------------------------------------------------------------


class ProgramVersionSerializer(ModelSerializer):

    class Meta:
        model = ProgramVersion
        read_only_fields = ('program', 'revision_number', 'display_name', 'description')


class ProgramSerializer(ModelSerializer):

    display_name = serializers.CharField(source='editing_version.display_name')
    description = serializers.CharField(source='editing_version.description')
    revision_number = serializers.CharField(source='editing_version.revision_number', read_only=True)
    is_locked = serializers.SerializerMethodField()

    top_compliance_list = serializers.SerializerMethodField()
    top_sync_interval_list = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ('id', 'display_name', 'description', 'revision_number', 'contact_name', 'contact_email', 'contact_phone_number', 'is_locked', 'cached_compliance_fraction', 'top_compliance_list', 'top_sync_interval_list', 'export_status', 'export_percentage', 'feature_enable_conditional_question_sets')

    def get_top_compliance_list(self, obj):
        return obj.cached_top_compliance_participant_id_list

    def get_top_sync_interval_list(self, obj):
        return obj.cached_longest_sync_interval_participant_id_list

    def get_is_locked(self, obj):
        return obj.is_locked()

    def create(self, validated_data):

        active_version_data = validated_data.pop('editing_version')

        program = Program.objects.create(**validated_data)

        program.editing_version.display_name = active_version_data['display_name']
        program.editing_version.description = active_version_data['description']
        program.editing_version.save()

        return program

    def update(self, instance, validated_data):

        instance.contact_name = validated_data['contact_name']
        instance.contact_email = validated_data['contact_email']
        instance.contact_phone_number = validated_data['contact_phone_number']
        instance.feature_enable_conditional_question_sets = validated_data['feature_enable_conditional_question_sets']
        instance.save()
        
        active_version_data = validated_data.pop('editing_version')

        instance.editing_version.display_name = active_version_data['display_name']
        instance.editing_version.description = active_version_data['description']
        instance.editing_version.save()

        return instance


class QuestionOptionSerializer(ModelSerializer):

    class Meta:
        model = QuestionOption
        read_only_fields = ('question',)


class ConditionalQuestionSetPredicateSerializer(ModelSerializer):

    desc = serializers.SerializerMethodField()
    target_question_set_name = serializers.SerializerMethodField()

    class Meta:
        model = ConditionalQuestionSetPredicate
        read_only_fields = ('question',)

    def get_desc(self, obj):
        return obj.get_desc()

    def get_target_question_set_name(self, obj):
        if obj.target_question_set is None:
            return "Target Question Set not selected."
        else:
            return obj.target_question_set.display_name


class QuestionSerializer(ModelSerializer):

    options = QuestionOptionSerializer(many=True)
    predicates = ConditionalQuestionSetPredicateSerializer(many=True)

    class Meta:
        model = Question
        read_only_fields = ('uuid',)

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        preds_data = validated_data.pop('predicates')
        question = Question.objects.create(**validated_data)

        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)

        for pred_data in preds_data:
            ConditionalQuestionSetPredicate.objects.create(question=question, **pred_data)

        return question

    def update(self, instance, validated_data):

        options = validated_data.pop('options')
        predicates = validated_data.pop('predicates')

        instance.question_text = validated_data['question_text']
        instance.question_tag = validated_data['question_tag']
        instance.randomise_option_order = validated_data['randomise_option_order']

        instance.min_value = validated_data['min_value']
        instance.min_label = validated_data['min_label']

        instance.max_value = validated_data['max_value']
        instance.max_label = validated_data['max_label']

        instance.save()

        option_ids = [item['id'] for item in options if 'id' in item]
        for option in instance.options.all():
            if option.id not in option_ids:
                option.delete()

        # Create or update page instances that are in the request
        for item in options:
            option = QuestionOption.objects.create(question=instance, **item)
            option.save()

        pred_ids = [item['id'] for item in predicates if 'id' in item]
        for pred in instance.predicates.all():
            if pred.id not in pred_ids:
                pred.delete()

        # Add/update predicates
        # Create or update page instances that are in the request
        for item in predicates:
            del item['target_option']
            target_question_set = item['target_question_set']
            target_value = item['target_value']
            target_min_value_incl = item['target_min_value_incl']
            target_max_value_incl = item['target_max_value_incl']

            if instance.question_type == Question.QUESTION_TYPE_SLIDER and target_min_value_incl == -1 and target_max_value_incl == -1:
                continue
            elif instance.question_type in [Question.QUESTION_TYPE_TEXT, Question.QUESTION_TYPE_RADIO, Question.QUESTION_TYPE_TEXT] and (target_value is None or len(target_value) == 0):
                continue

            pred = ConditionalQuestionSetPredicate.objects.create(question=instance, **item)
            pred.save()

        return instance


class QuestionSetSerializer(ModelSerializer):

    questions = QuestionSerializer(many=True, read_only=True)
    is_jump_target = serializers.SerializerMethodField()

    class Meta:
        model = QuestionSet
        read_only_fields = ('uuid', 'group')

    def get_is_jump_target(self, obj):
        has_predicates = obj.predicates.all().exists()
        return has_predicates


class ScheduleSerializer(ModelSerializer):

    class Meta:
        model = Schedule
        read_only_fields = ('uuid',)


class EventLogSerializer(ModelSerializer):

    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = EventLog


class SurveySerializer(ModelSerializer):

    question_sets = QuestionSetSerializer(many=True, read_only=True)
    schedule_name = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        read_only_fields = ('uuid', 'participants', 'schedule_name',)

    def get_schedule_name(self, obj):
        return obj.schedule.display_name if obj.schedule else 'Not set'

class ProgramParticipantSerializer(ModelSerializer):

    compliance_percentage = serializers.SerializerMethodField()

    def get_compliance_percentage(self, obj):
        return int(obj.cached_compliance_fraction * 100)

    class Meta:
        model = ProgramParticipantBridge
        fields = ('program_participant_status', 'use_custom_start_stop_time', 'custom_start_hour', 'custom_start_minute', 'custom_stop_hour', 'custom_stop_minute', 'compliance_percentage', 'app_version_string', 'app_version_number', 'app_platform_name', 'cached_received_answer_set_count', 'cached_answered_answer_set_count', 'cached_last_sync_timestamp', 'cached_last_upload_timestamp', 'is_running_latest_app_version')


class ParticipantSerializer(ModelSerializer):

    assigned_surveys = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()

    def get_assigned_surveys(self, obj):
        serializer = SurveySerializer(obj.surveys.filter(program_version=self.context['program_version']), many=True, context=self.context)
        return serializer.data

    def get_info(self, obj):
        bridge = obj.program_profiles.get(program__pk=self.context['program_id'])
        serializer = ProgramParticipantSerializer(bridge, context=self.context)
        return serializer.data

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'assigned_surveys', 'info')


class AdminSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')


class AnswerSerializer(ModelSerializer):

    answer_display = serializers.SerializerMethodField()
    linked_question = serializers.SerializerMethodField()

    def get_linked_question(self, obj):
        return QuestionSerializer(obj.question).data

    def get_answer_display(self, obj):

        if obj.question.question_type in (Question.QUESTION_TYPE_RADIO, Question.QUESTION_TYPE_MULTICHOICE):

            obj.link_to_option()

            return obj.answered_option.label if obj.answered_option else "[ DB ERROR DETECTED ]"
        elif obj.question.question_type == Question.QUESTION_TYPE_SLIDER:
            return '{} (Min: {}, Max: {})'.format(obj.answer_value, obj.question.min_value, obj.question.max_value)
        else:
            return obj.answer_value

    class Meta:
        model = Answer
        read_only_fields = ('set',)


class AnswerSetSerializer(ModelSerializer):

    answers = AnswerSerializer(many=True, required=False)
    username = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()
    survey_name = serializers.SerializerMethodField()

    def get_version(self, obj):
        return obj.program_version.revision_number

    def get_username(self, obj):
        return obj.user.username

    def get_survey_name(self, obj):
        return obj.survey.display_name

    class Meta:
        model = AnswerSet
        fields = ('id', 'user', 'completed_timestamp', 'created_timestamp', 'expiry_timestamp', 'delivery_timestamp', 'uploaded_timestamp', 'survey_name', 'survey', 'iteration', 'program_version', 'answers', 'version', 'username', 'timezone', 'uuid')
        read_only_fields = ('user', 'uuid', 'has_answers')

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        set = AnswerSet.objects.create(**validated_data)

        for answer_data in answers:
            answer = Answer.objects.create(set=set, **answer_data)
            answer.link_to_option()

        return set


class ProgramInviteSerializer(ModelSerializer):

    class Meta:
        model = ProgramInvite
        read_only_fields = ('inviting_user',)

# -----------------------------------------------------------------------------
#  ViewSet
# -----------------------------------------------------------------------------


class ProgramViewSet(ModelViewSet):
    model = Program
    serializer_class = ProgramSerializer

    def get_queryset(self):
        user = self.request.user

        archived_only = int(self.request.query_params.get('archived_only', '0')) == 1

        qs = user.administered_programs.all()

        if archived_only:
            qs = qs.filter(status=Program.PROGRAM_STATUS_ARCHIVED)
        else:
            qs = qs.filter(status=Program.PROGRAM_STATUS_ACTIVE)

        return qs

    @detail_route(methods=['get'])
    def participants(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        filter = request.GET.get('f', None)

        if filter is not None:
            uname = Q(username__contains=filter)
            email = Q(email__contains=filter)

            participants = program.participants.filter(uname | email).order_by('-pk')
        else:
            participants = program.participants.all().order_by('-pk')

        return Response(ParticipantSerializer(participants, many=True, context={'program_version': program.editing_version, 'program_id': program.pk}).data)

    @detail_route(methods=['get'])
    def admins(self, request, pk=None):
        admins = Program.objects.get(pk=pk).admins.all()
        return Response(AdminSerializer(admins, many=True).data)

    @detail_route(methods=['get'])
    def surveys(self, request, pk=None):
        program = Program.objects.get(pk=pk)
        return Response(SurveySerializer(program.editing_version.surveys.filter(status=Survey.SURVEY_STATUS_ACTIVE), many=True).data)

    @detail_route(methods=['get'])
    def sets(self, request, pk=None):
        program = Program.objects.get(pk=pk)
        return Response(QuestionSetSerializer(program.editing_version.question_sets.filter(status=QuestionSet.QUESTION_SET_STATUS_ACTIVE), many=True).data)

    @detail_route(methods=['get', 'delete'])
    def schedules(self, request, pk=None):
        program = Program.objects.get(pk=pk)
        return Response(ScheduleSerializer(program.editing_version.schedules.all(), many=True).data)

    @detail_route(methods=['get'])
    def activity(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        filter = request.GET.get('filter', None)

        logs = EventLog.objects.filter(program_version__program=program).order_by('-timestamp')

        if filter == 'admin':
            logs = logs.filter(log_type__in=[EventLog.LOG_PROGRAM_DATA_EXPORT, EventLog.LOG_PROGRAM_EDIT, EventLog.LOG_PROGRAM_PUBLISH])
        elif filter == 'user':
            logs = logs.filter(log_type__in=[EventLog.LOG_NOTE, EventLog.LOG_APP_SYNC, EventLog.LOG_APP_DATA_UPLOAD, EventLog.LOG_APP_UPGRADE])

        logs = logs[:32]

        return Response(EventLogSerializer(logs, many=True).data)

    @detail_route(methods=['get', 'delete'])
    def responses(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        qs = AnswerSet.unique_objects.filter(program_version__program=program).order_by('-delivery_timestamp',)

        user_id = int(request.GET.get('u', -1))
        if user_id != -1:
            qs = qs.filter(user__pk=user_id)

        try:
            sort_by = request.GET.get('s', '')
            if sort_by != '':
                AnswerSet._meta.get_field(sort_by)
                qs = qs.order_by('-' + sort_by)
        except FieldDoesNotExist:
            pass

        p = Paginator(qs, 80)
        page_num = int(request.GET.get('p', 1))
        page = p.page(page_num)
        res = {
            "cur_page": page_num,
            "num_pages": p.num_pages,
            "items": AnswerSetSerializer(page.object_list, many=True).data
        }

        return Response(res)

    @detail_route(methods=['get'])
    def invites(self, request, pk=None):
        program = Program.objects.get(pk=pk)
        return Response(ProgramInviteSerializer(program.invitations.filter(has_been_confirmed=False), many=True).data)

    @detail_route(methods=['post'])
    def export_data(self, request, pk=None):

        program = Program.objects.get(pk=pk)
        email_on_completion = request.DATA.get('email_on_completion', None)
        archive_password = request.DATA.get('archive_password', None)

        program.export_status = Program.EXPORT_STATUS_IN_PROGRESS
        program.export_percentage = 0
        program.export_initiator_user = request.user
        program.save()

        try:
            tasks.export_data.apply_async(args=(program.pk, request.user.pk, email_on_completion, archive_password), queue='export')
        except Exception:
            program.export_status = Program.EXPORT_STATUS_READY
            program.save()

        return Response({'status': 'ok'})

    @detail_route(methods=['get'])
    def export_status(self, request, pk=None):

        program = Program.objects.get(pk=pk)

        return Response({
            'export_status': program.export_status,
            'export_percentage': program.export_percentage
        })

    @detail_route(methods=['post'])
    def create_new_version(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        with transaction.atomic():
            program.create_new_version()
            EventLog.log_program_unlocked_event(program, request.user)

        return Response(ProgramSerializer(program).data)

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        with transaction.atomic():
            program.clone()

        return Response(ProgramSerializer(program).data)

    @detail_route(methods=['post'])
    def archive(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        with transaction.atomic():
            program.status = Program.PROGRAM_STATUS_ARCHIVED
            program.save()

        # Notify everyone
        bridges = ProgramParticipantBridge.objects.filter(program=program)
        for bridge in bridges:
            bridge.force_data_update = True
            bridge.save()
            bridge.send_content_update_message()

        return Response(ProgramSerializer(program).data)

    @detail_route(methods=['post'])
    def unarchive(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        with transaction.atomic():
            program.status = Program.PROGRAM_STATUS_ACTIVE
            program.save()

        # Notify everyone
        bridges = ProgramParticipantBridge.objects.filter(program=program)
        for bridge in bridges:
            bridge.force_data_update = True
            bridge.save()
            bridge.send_content_update_message()

        return Response(ProgramSerializer(program).data)

    @detail_route(methods=['post'])
    def publish_latest_draft(self, request, pk=None):

        with transaction.atomic():
            program = Program.objects.get(pk=pk)

            if program.is_locked():
                raise Exception("You do not have an editing version active")

            editing_version = program.editing_version
            editing_version.editing_status = ProgramVersion.EDITING_STATUS_PUBLISHED
            editing_version.save()

            program.active_version = program.editing_version
            program.save()

        # Notify everyone
        bridges = ProgramParticipantBridge.objects.filter(program=program)
        for bridge in bridges:
            bridge.send_content_update_message()

        EventLog.log_program_published_event(program, request.user)

        return Response(ProgramSerializer(program).data)

    @detail_route(methods=['put', 'post'])
    def set_program_participant_status(self, request, pk=None):
        program = Program.objects.get(pk=pk)
        user_id = request.GET.get('user')
        user = User.objects.get(pk=user_id)

        bridge = ProgramParticipantBridge.objects.get(user=user, program=program)
        bridge.program_participant_status = request.data['status']
        bridge.save()

        return Response({})

    @detail_route(methods=['put', 'post'])
    def reset_participant_compliance(self, request, pk=None):
        program = Program.objects.get(pk=pk)
        user_id = request.DATA.get('user')
        user = User.objects.get(pk=user_id)

        bridge = ProgramParticipantBridge.objects.get(user=user, program=program)
        bridge.compliance_start_timestamp = arrow.utcnow().datetime
        bridge.save()

        tasks.update_compliance_for_program(program.pk)

        return Response({})

    @detail_route(methods=['put', 'post'])
    def reset_participant_iterations(self, request, pk=None):

        user_id = request.DATA.get('user')
        user = User.objects.get(pk=user_id)

        survey_uuid = request.DATA.get('survey')

        state = ProgramParticipantState.get_for_user_and_survey_uuid(user, survey_uuid)
        state.current_iteration = 0
        state.save()

        return Response({})

    @detail_route(methods=['post', 'put'])
    def get_survey_info(self, request, pk=None):
        program = Program.objects.get(pk=pk)

        user_id = request.DATA.get('user')
        user = User.objects.get(pk=user_id)

        survey_uuid = request.DATA.get('survey')
        survey = Survey.objects.get(program_version=program.editing_version, uuid=survey_uuid)

        state = ProgramParticipantState.get_for_user_and_survey_uuid(user, survey_uuid)

        return Response({
            'current_iteration': state.current_iteration,
            'max_iterations': survey.max_iterations
        })

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.admins.add(self.request.user)


class ProgramVersionViewSet(ModelViewSet):
    model = ProgramVersion
    serializer_class = ProgramVersionSerializer

    def get_queryset(self):
        user = self.request.user
        return ProgramVersion.objects.filter(program__user=user)


class QuestionSetViewSet(ModelViewSet):
    model = QuestionSet
    serializer_class = QuestionSetSerializer

    def get_queryset(self):
        return QuestionSet.objects.filter(status=QuestionSet.QUESTION_SET_STATUS_ACTIVE)

    @detail_route(methods=['get'])
    def questions(self, request, pk=None):
        set = QuestionSet.objects.get(pk=pk)
        return Response(Question(set.questions.all(), many=True).data)

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        set = QuestionSet.objects.get(pk=pk)
        new_set = QuestionSet.clone(set, set.program_version)
        new_set.uuid = str(uuid.uuid4())
        new_set.save()
        return Response(QuestionSetSerializer(new_set).data)

    @detail_route(methods=['post'])
    def archive(self, request, pk=None):
        question_set = QuestionSet.objects.get(pk=pk)

        with transaction.atomic():
            question_set.status = QuestionSet.QUESTION_SET_STATUS_ARCHIVED
            question_set.save()

        return Response({})

    def perform_create(self, serializer):
        from uuid import uuid4
        uuid = str(uuid4())
        instance = serializer.save(uuid=uuid)


class QuestionViewSet(ModelViewSet):
    model = Question
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.all()

    def perform_create(self, serializer):
        from uuid import uuid4
        uuid = str(uuid4())
        instance = serializer.save(uuid=uuid)


class QuestionOptionViewSet(ModelViewSet):
    model = QuestionOption
    serializer_class = QuestionOptionSerializer

    def get_queryset(self):
        return QuestionOption.objects.all()


class SurveyViewSet(ModelViewSet):
    model = Survey
    serializer_class = SurveySerializer
    queryset = Survey.objects.filter(status=Survey.SURVEY_STATUS_ACTIVE)

    @detail_route(methods=['put', 'post'])
    def selected_sets(self, request, pk=None):
        survey = Survey.objects.get(pk=pk)
        ids = request.data

        survey.question_sets.clear()

        for id in ids:
            survey.question_sets.add(id)

        survey.save()

        return Response({})

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        survey = Survey.objects.get(pk=pk)
        new_survey = Survey.clone(survey, survey.program_version)
        new_survey.uuid = str(uuid.uuid4())
        new_survey.save()
        return Response(SurveySerializer(new_survey).data)

    @detail_route(methods=['post'])
    def archive(self, request, pk=None):
        survey = Survey.objects.get(pk=pk)

        with transaction.atomic():
            survey.status = Survey.SURVEY_STATUS_ARCHIVED

            for participant in survey.participants.all():
                survey.participants.remove(participant)

            survey.save()

        return Response(SurveySerializer(survey).data)

    @detail_route(methods=['get'])
    def structure_graph(self, request, pk=None):
        survey = Survey.objects.get(pk=pk)

        from graphviz import Digraph

        graph = Digraph(comment='Survey Structure', format='png', engine='dot', edge_attr={'style': 'dashed'})

        # Go through each QS in the survey and add find all the questi
        for qs in survey.question_sets.all():
            self.process_question_set(graph, qs)

        return HttpResponse(graph.pipe(), content_type='image/png')

    def process_question_set(self, graph, qs):

        graph.node(str(qs.pk), qs.display_name)

        for question in qs.questions.all():
            
            for pred in question.predicates.all():
                graph.edge(str(qs.pk), str(pred.target_question_set.pk), pred.get_conditional_desc())
                self.process_question_set(graph, pred.target_question_set)

    def perform_create(self, serializer):
        from uuid import uuid4
        uuid = str(uuid4())
        instance = serializer.save(uuid=uuid)


class ScheduleViewSet(ModelViewSet):

    model = Schedule
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        user = self.request.user
        return Schedule.objects.all()

    def perform_create(self, serializer):
        from uuid import uuid4
        uuid = str(uuid4())
        instance = serializer.save(uuid=uuid)


class EventLogViewSet(ModelViewSet):

    model = EventLog

    def get_queryset(self):
        user = self.request.user
        return Schedule.objects.filter(program__user=user)


class AnswerSetViewSet(ModelViewSet):
    model = AnswerSet
    serializer_class = AnswerSetSerializer

    def get_queryset(self):
        return AnswerSet.unique_objects.all()

    def perform_create(self, serializer):
        from uuid import uuid4
        uuid = str(uuid4())
        user = self.request.user
        instance = serializer.save(uuid=uuid, user=user)


class AnswerViewSet(ModelViewSet):
    model = Answer
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)


class ParticipantViewSet(ReadOnlyModelViewSet):

    model = User
    serializer_class = ParticipantSerializer
    read_only = True

    def get_queryset(self):
        return User.objects.all()

    @detail_route(methods=['put', 'post'])
    def profile(self, request, pk=None):

        user = User.objects.get(pk=pk)

        # Update the status
        program_id = request.data['program']
        program = Program.objects.get(pk=program_id)

        info = request.data['info']
        status = info['program_participant_status']

        bridge = ProgramParticipantBridge.objects.get(user=user, program=program)

        if status != bridge.program_participant_status or \
            bridge.custom_start_hour != info['custom_start_hour'] or \
            bridge.custom_start_minute != info['custom_start_minute'] or \
            bridge.custom_stop_hour != info['custom_stop_hour'] or \
            bridge.custom_stop_minute != info['custom_stop_minute'] or \
            bridge.use_custom_start_stop_time != info['use_custom_start_stop_time']:

            needs_update = True
        else:
            needs_update = False


        bridge.custom_start_hour = info['custom_start_hour']
        bridge.custom_start_minute = info['custom_start_minute']

        bridge.custom_stop_hour = info['custom_stop_hour']
        bridge.custom_stop_minute = info['custom_stop_minute']

        bridge.use_custom_start_stop_time = info['use_custom_start_stop_time']

        bridge.program_participant_status = status
        bridge.force_data_update = True

        bridge.save()

        if needs_update:
            bridge.send_content_update_message()

        #
        existing = user.surveys.filter(program_version=program.editing_version)

        for ex in existing:
            user.surveys.remove(ex)

        # Setup the surveys
        ids = request.data['assigned_surveys']

        for id in ids:
            user.surveys.add(id)
            Survey.objects.get(pk=id)

        return Response({})

    @detail_route(methods=['put', 'post'])
    def status(self, request, pk=None):
        user = User.objects.get(pk=pk)
        return Response({})

    @list_route(
        methods=['post'],
        permission_classes=[AllowAny],
        authentication_classes=[]
    )
    def reset_password(self, request):

        if request.DATA.get('email'):
            form = ResetPasswordForm({'email': request.DATA.get('email')})

            if form.is_valid():
                form.save(request)
                return Response(status=200)

        return Response(status=400)


class ProgramInviteViewSet(ModelViewSet):

    model = ProgramInvite
    serializer_class = ProgramInviteSerializer

    def get_queryset(self):
        return ProgramInvite.objects.all()

    def perform_create(self, serializer):

        data = serializer.validated_data

        username = None
        password = None

        # See if the email address already exists
        try:
            existing_user = User.objects.get(email__iexact=data['email_address'], is_active=True)
        except User.DoesNotExist:
            existing_user = None

        invite_type = data['invitation_type']

        if invite_type == ProgramInvite.INVITE_TYPE_PARTICIPANT:

            if existing_user is None:
                username = '{0:07}'.format(random.randint(1, 10000000))
                password = 'foo'
            else:
                username = existing_user.username

        elif invite_type == ProgramInvite.INVITE_TYPE_TEAM:

            if existing_user is None:
                username = '{0:07}'.format(random.randint(1, 10000000))
                password = 'foo'
            else:
                username = existing_user.username

        require_email_confirmation = data['require_email_confirmation']

        invite = serializer.save(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email_address=data['email_address'],
            phone_number=data['phone_number'],
            require_email_confirmation=require_email_confirmation,
            inviting_user=self.request.user,
            invitation_type=invite_type,
            is_existing_user=existing_user is not None,
            username=username,
            password=password
        )

        # Force confirmation later
        if not require_email_confirmation:
            tasks.confirm_invite_and_get_welcome_url(invite)
            invite.save()

    @detail_route(methods=['post'])
    def confirm(self, request, pk=None):
        invite = ProgramInvite.objects.get(pk=pk)
        tasks.confirm_invite_and_get_welcome_url(invite)
        invite.save()
        return Response({})

    @detail_route(methods=['post'])
    def cancel(self, request, pk=None):
        invite = ProgramInvite.objects.get(pk=pk)
        invite.delete()
        return Response({})


class SyncView(APIView):

    def post(self, request, format=None):

        has_changes = False

        if isinstance(request.data, list):
            has_changes = False
            app_id = settings.DEFAULT_APP_ID
            app_build_number = 1
            app_version_string = "1.0.0"
            program_versions = request.data
            push_token = None
            app_platform_name = '?'
        else:
            has_changes = request.data['force_update'] if 'force_update' in request.data else False
            app_id = request.data.get('app_id', settings.DEFAULT_APP_ID)
            app_build_number = request.data['app_build_number']
            app_version_string = request.data['app_version_string']
            program_versions = request.data['program_versions']
            push_token = request.data['push_token']
            app_platform_name = request.data['app_platform']

        program_info = {}

        for item in program_versions:
            program_info[item['program']] = item['version']

        program_items = []

        user = request.user
        programs = user.participated_programs.all()

        for program in programs:

            bridge = ProgramParticipantBridge.objects.get(user=user, program=program)

            if bridge.force_data_update:
                has_changes = True
                bridge.force_data_update = False

            bridge.app_id = app_id
            bridge.app_version_number = app_build_number
            bridge.app_version_string = app_version_string
            bridge.device_push_token = push_token
            bridge.app_platform_name = app_platform_name
            bridge.cached_last_sync_timestamp = arrow.utcnow().datetime

            # Check if the user is running the latest available version of the app
            app_update_config = AppUpdateConfig.objects.get(platform_id=app_platform_name)
            bridge.is_running_latest_app_version = (app_build_number == app_update_config.build_number)

            bridge.save()

            if bridge.program_participant_status != ProgramParticipantBridge.PROGRAM_PARTICIPANT_STATUS_ACTIVE:
                continue

            if program.active_version is None:
                continue

            if program.status != Program.PROGRAM_STATUS_ACTIVE:
                continue

            active_version = program.active_version

            if program.pk in program_info:
                if program_info[program.pk] < active_version.revision_number:
                    has_changes = True
            else:
                has_changes = True

            survey_items = []

            for survey in user.surveys.filter(program_version=active_version, program_version__program=program):

                # Get all the active question sets for the survey
                survey_question_set_ids = survey.question_sets.filter(status=QuestionSet.QUESTION_SET_STATUS_ACTIVE).values_list('pk', flat=True)
                survey_question_set_qs = QuestionSet.objects.filter(pk__in=survey_question_set_ids)

                # Output a list of these question sets
                question_set_items = self.build_question_set_list(survey_question_set_qs)

                # Get a list of all jump targets from the Conditional Question Set Predicates for the survey
                conditional_question_set_ids = ConditionalQuestionSetPredicate.objects.filter(question__set__group=survey).values_list('target_question_set', flat=True)

                # Exclude any question sets we have already included
                conditional_question_set_qs = QuestionSet.objects.filter(pk__in=conditional_question_set_ids).exclude(pk__in=survey_question_set_ids)

                # Output a list of these question sets
                conditional_question_set_items = self.build_question_set_list(conditional_question_set_qs)

                state = ProgramParticipantState.get_for_user_and_survey_uuid(user, survey.uuid)

                schedule = survey.schedule

                if bridge.use_custom_start_stop_time:
                    schedule_start_hour = bridge.custom_start_hour
                    schedule_start_minute = bridge.custom_start_minute

                    schedule_stop_hour = bridge.custom_stop_hour
                    schedule_stop_minute = bridge.custom_stop_minute

                else:
                    schedule_start_hour = schedule.start_time_hours if schedule else 0
                    schedule_start_minute = schedule.start_time_minutes if schedule else 0

                    schedule_stop_hour = schedule.stop_time_hours if schedule else 0
                    schedule_stop_minute = schedule.stop_time_minutes if schedule else 0

                survey_data = {
                    "id": survey.id,
                    "display_name": survey.display_name,
                    "randomise_set_order": survey.randomise_set_order,
                    "max_iterations": survey.max_iterations,
                    "current_iteration": state.current_iteration+1,
                    "trigger_mode": survey.trigger_mode,
                    "question_sets": question_set_items,
                    "conditional_question_sets": conditional_question_set_items,

                    "schedule_is_active": schedule is not None,
                    "schedule_delivery_interval_minutes": schedule.interval_minutes if schedule else 10000,
                    "schedule_delivery_variation_minutes": schedule.offset_plus_minus_minutes if schedule else 0,
                    "schedule_survey_expiry_minutes": schedule.expiry_minutes if schedule else 10000,

                    "schedule_start_sending_at_hour": schedule_start_hour,
                    "schedule_start_sending_at_minute": schedule_start_minute,

                    "schedule_stop_sending_at_hour": schedule_stop_hour,
                    "schedule_stop_sending_at_minute": schedule_stop_minute,

                    "schedule_allow_monday": schedule.allow_monday if schedule else False,
                    "schedule_allow_tuesday": schedule.allow_tuesday if schedule else False,
                    "schedule_allow_wednesday": schedule.allow_wednesday if schedule else False,
                    "schedule_allow_thursday": schedule.allow_thursday if schedule else False,
                    "schedule_allow_friday": schedule.allow_friday if schedule else False,
                    "schedule_allow_saturday": schedule.allow_saturday if schedule else False,
                    "schedule_allow_sunday": schedule.allow_sunday if schedule else False
                }

                if survey.trigger_mode == Survey.TRIGGER_MODE_ADHOC or \
                        (survey.trigger_mode == Survey.TRIGGER_MODE_SCHEDULED and survey.schedule is not None):
                    survey_items.append(survey_data)

            program_data = {
                'id': program.pk,
                'version_id': active_version.pk,
                'version_number': active_version.revision_number,
                'display_name': active_version.display_name,
                'description': active_version.description,

                "contact_name": program.contact_name,
                "contact_email": program.contact_email,
                "contact_number": program.contact_phone_number,

                "surveys": survey_items
            }

            program_items.append(program_data)

            EventLog.log_sync_event_for_user(program, user, True, has_changes)

        sync_data = {
            'programs': program_items
        }

        if has_changes:
            return Response(sync_data)
        else:
            return Response(status=304)

    def build_question_set_list(self, question_sets_qs):

        question_set_items = []

        for question_set in question_sets_qs:

            question_items = []

            for question in question_set.questions.all():

                option_items = []
                predicate_items = []

                for option in question.options.all():

                    option_data = {
                        "id": option.pk,
                        "label": option.label,
                        "value": option.value
                    }

                    option_items.append(option_data)

                for predicate in question.predicates.all():

                    predicate.link_to_option_if_unlinked()

                    predicate_data = {
                        "id": predicate.pk,
                        "question": question.pk,
                        "question_type": question.question_type,
                        "action": predicate.action,
                        "enabled": predicate.enabled,
                        "target_question_set": predicate.target_question_set.pk,
                        "target_value": predicate.target_value,
                        "target_option": predicate.target_option.pk if predicate.target_option is not None else -1,
                        "target_min_value_incl": predicate.target_min_value_incl,
                        "target_max_value_incl": predicate.target_max_value_incl
                    }

                    predicate_items.append(predicate_data)

                question_data = {
                    "id": question.pk,
                    "randomise_option_order": question.randomise_option_order,
                    "question_type": question.question_type,
                    "question_text": question.question_text,
                    "minimum_value": question.min_value,
                    "minimum_label": question.min_label,
                    "maximum_value": question.max_value,
                    "maximum_label": question.max_label,
                    "options": option_items,
                    "predicates": predicate_items
                }

                question_items.append(question_data)

            question_set_data = {
                "id": question_set.pk,
                "randomise_question_order": question_set.randomise_question_order,
                "questions": question_items,
            }

            question_set_items.append(question_set_data)

        return question_set_items


class TestPushView(APIView):

    def get(self, request, format=None):

        bridge_id = request.GET.get('bid')
        bridge = ProgramParticipantBridge.objects.get(pk=bridge_id)

        device = bridge.get_device()

        if device:
            msg = 'Test Push'
            bridge.send_content_update_message()

        return Response({})


class UpdateStatisticsView(APIView):

    def get(self, request, format=None):

        tasks.update_compliance()

        return Response({})
