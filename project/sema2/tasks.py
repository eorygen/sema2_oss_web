import contextlib
import csv
import multiprocessing
import os
import tempfile
import zipfile

import gc

import shutil
from celery import shared_task, task
import arrow
from datetime import timedelta, datetime
import time
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from template_email import TemplateEmail
from sema2 import tokens
from sema2.models import ProgramInvite, AnswerSet, ProgramParticipantBridge, Program, Question, Answer, QuestionOption, \
    ProgramParticipantState, ProgramVersion
from sema2.tokens import create_invite_token
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def generate_confirmation_token(invitation_id):

    invite = ProgramInvite.objects.get(pk=invitation_id)
    confirmation_token = create_invite_token(invitation_id, invite.invitation_type, 14, settings.JWT_SECRET)
    return invite, confirmation_token


def send_participant_invite(invitation_id):

    invite, confirmation_token = generate_confirmation_token(invitation_id)

    current_site = Site.objects.get_current()

    context = {
        'first_name': invite.first_name,
        'program_name': invite.program.editing_version.display_name,
        'enrollment_url': "http://{}{}".format(current_site.domain, reverse('confirm-invite', kwargs={
            'confirmation_token': confirmation_token
        })),
        'password_change_url': "http://{}/accounts/password/reset/".format(current_site.domain),
        'is_existing_user': invite.is_existing_user,
        'username': invite.username,
        'password': invite.password
    }

    if invite.invitation_type == ProgramInvite.INVITE_TYPE_PARTICIPANT:
        template = 'email/participant_invite.html'
    else:
        template = 'email/team_invite.html'

    email = TemplateEmail(template=template, context=context, to=[invite.email_address], from_email='sema@sema-surveys.com')
    email.send()


def confirm_invite_and_get_welcome_url(invitation):

    if not invitation.is_existing_user and not invitation.has_been_confirmed:

        # Create the user
        user = User.objects.create_user(
            username=invitation.username,
            email=invitation.email_address,
            password=invitation.password
        )
    else:
        user = User.objects.get(username=invitation.username)

    if invitation.invitation_type == tokens.INVITE_TOKEN_TYPE_PARTICIPANT:

        if not invitation.has_been_confirmed:

            # Add them to the participant group
            from django.contrib.auth.models import Group
            g = Group.objects.get(name='sema_participant')
            g.user_set.add(user)
            user.save()

            # Add them to the program
            if not ProgramParticipantBridge.objects.filter(user=user, program=invitation.program).exists():
                ProgramParticipantBridge.objects.create(
                    user=user,
                    program=invitation.program
                )

            # Assign all of the surveys in the program to them (for now)
            from models import Survey
            for survey in invitation.program.editing_version.surveys.filter(status=Survey.SURVEY_STATUS_ACTIVE):
                survey.participants.add(user)

                # Create the required state
                state = ProgramParticipantState.get_for_user_and_survey_uuid(user, survey.uuid)

        url = "{}?welcome=1".format(reverse('home'))

    elif invitation.invitation_type == tokens.INVITE_TOKEN_TYPE_ADMIN:

        if not invitation.has_been_confirmed:

            # Add them to the participant group
            from django.contrib.auth.models import Group
            g = Group.objects.get(name='sema_admin')
            g.user_set.add(user)
            user.save()

            # Add them as an admin
            invitation.program.admins.add(user)

        url = "{}?welcome=1".format(reverse('dashboard', kwargs={'program_id': invitation.program.pk}))

    invitation.has_been_confirmed = True

    return url


@task(name='tasks.update_compliance')
def update_compliance():

    programs = Program.objects.all()

    logger.info("Updating compliance for {} programs".format(len(programs)))

    for program in programs:

        logger.info("Updating compliance for program id: {}".format(program.editing_version.display_name))

        program_frac = 0.0
        count = 0

        participants = program.participants.all()

        for participant in participants:
            compliance_frac, include_in_stats = calculate_participant_compliance(participant.pk, program.pk)

            if include_in_stats:
                program_frac += compliance_frac
                count += 1


        # Set the compliance
        if count > 0:
            program.cached_compliance_fraction = float(program_frac) / float(count)
        else:
            program.cached_compliance_fraction = 0

        logger.info("Compliance for program id: {} = {}".format(program.editing_version.display_name, program.cached_compliance_fraction))

        # Calculate the top x compliance
        top_compliance = ProgramParticipantBridge.objects.filter(program=program, program_participant_status=ProgramParticipantBridge.PROGRAM_PARTICIPANT_STATUS_ACTIVE).order_by('cached_compliance_fraction')[:10]
        logger.info("Found {} top compliance candidates".format(len(top_compliance)))

        list = []
        for item in top_compliance:

            logger.info("FOO")

            list.append({
                'compliance': item.cached_compliance_fraction * 100,
                'email': item.user.email
            })

        program.cached_top_compliance_participant_id_list = list

        # Calculate the top interval
        top_interval = ProgramParticipantBridge.objects.filter(program=program, program_participant_status=ProgramParticipantBridge.PROGRAM_PARTICIPANT_STATUS_ACTIVE).order_by('-cached_last_sync_interval_seconds')[:5]
        logger.info("Found {} top interval candidates".format(len(top_interval)))

        list = []
        for item in top_interval:

            logger.info("BAR")

            list.append({
                'interval': item.cached_last_sync_timestamp,
                'email': item.user.email
            })

        program.cached_longest_sync_interval_participant_id_list = list

        program.save()

@task(name='tasks.update_compliance_for_program')
def update_compliance_for_program(program_id):

    program = Program.objects.get(pk=program_id)

    logger.info("Updating compliance for program id: {}".format(program.editing_version.display_name))

    program_frac = 0.0
    count = 0
    participants = program.participants.all()

    for participant in participants:
            compliance_frac, include_in_stats = calculate_participant_compliance(participant.pk, program.pk)

            if include_in_stats:
                program_frac += compliance_frac
                count += 1

    # Set the compliance
    if count > 0:
        program.cached_compliance_fraction = float(program_frac) / float(count)
    else:
        program.cached_compliance_fraction = 0

    # Calculate the top x compliance
    top_compliance = ProgramParticipantBridge.objects.filter(program=program, program_participant_status=ProgramParticipantBridge.PROGRAM_PARTICIPANT_STATUS_ACTIVE).order_by('-cached_compliance_fraction')[:5]
    logger.info("Found {} top compliance candidates".format(len(top_compliance)))

    list = []
    for item in top_compliance:

        logger.info("FOO")

        list.append({
            'compliance': item.cached_compliance_fraction * 100,
            'email': item.user.email
        })

    program.cached_top_compliance_participant_id_list = list

    # Calculate the top interval
    top_interval = ProgramParticipantBridge.objects.filter(program=program, program_participant_status=ProgramParticipantBridge.PROGRAM_PARTICIPANT_STATUS_ACTIVE).order_by('-cached_last_sync_interval_seconds')[:5]
    logger.info("Found {} top interval candidates".format(len(top_interval)))

    list = []
    for item in top_interval:

        logger.info("BAR")

        list.append({
            'interval': item.cached_last_sync_interval_seconds,
            'email': item.user.email
        })

    program.cached_longest_sync_interval_participant_id_list = list

    program.save()


@task(name='tasks.calculate_participant_compliance')
def calculate_participant_compliance(participant_id, program_id):

    try:
        logger.info("Updating compliance for user id: {}".format(participant_id))

        completed = 0
        uploaded = 0

        bridge = ProgramParticipantBridge.objects.get(user__pk=participant_id, program__pk=program_id)

        range_end = arrow.utcnow().datetime

        if bridge.compliance_start_timestamp is not None:
            range_start = bridge.compliance_start_timestamp
        else:
            range_start = bridge.user.date_joined

        answer_sets = AnswerSet.unique_objects.filter(program_version__program__pk=program_id, user__pk=participant_id, delivery_timestamp__range=(range_start, range_end))
        logger.info("Found {} answer sets for user id {}".format(len(answer_sets), participant_id))

        for answer_set in answer_sets:

            uploaded += 1

            if answer_set.has_answers:
                completed += 1

            time.sleep(0.1)

        bridge.cached_answered_answer_set_count = completed
        bridge.cached_received_answer_set_count = uploaded

        logger.info("Counted {} recvd, {} answered for user id {}".format(
            bridge.cached_received_answer_set_count,
            bridge.cached_answered_answer_set_count,
            participant_id)
        )

        if bridge.cached_received_answer_set_count > 0:
            bridge.cached_compliance_fraction = float(bridge.cached_answered_answer_set_count) / float(bridge.cached_received_answer_set_count)
        else:
            bridge.cached_compliance_fraction = 0

        # Get the latest upload time
        latest_upload = AnswerSet.unique_objects.filter(user__pk=participant_id).order_by('-uploaded_timestamp').first()

        if latest_upload:
            bridge.cached_last_upload_timestamp = latest_upload.uploaded_timestamp

        if bridge.cached_last_sync_timestamp is not None:
            # Interval since last sync
            bridge.cached_last_sync_interval_seconds = (arrow.utcnow().datetime - bridge.cached_last_sync_timestamp).total_seconds()

        logger.info("Compliance updated for user id {} = {}, interval {}".format(participant_id, bridge.cached_compliance_fraction, bridge.cached_last_sync_interval_seconds))

        bridge.save()

        return bridge.cached_compliance_fraction, bridge.program_participant_status == ProgramParticipantBridge.PROGRAM_PARTICIPANT_STATUS_ACTIVE

    except Exception:
        logger.exception("Error updating compliance for user id {}".format(participant_id))


def append_text_answers(answer_set, question, row):

    rt = 0

    answer = answer_set.answers.filter(question=question).first()
    if answer:
        ascii_value = answer.answer_value.encode('ascii', 'ignore').decode('ascii')
        row.append(ascii_value)
        rt += answer.reaction_time_ms
    else:
        row.append('')

    # add the response time
    row.append(rt)

    return row, rt


def append_multichoice_answers(answer_set, question, row):

    rt = 0

    is_answered = answer_set.answers.filter(question=question).count() > 0

    if not is_answered:
        options = question.options.all().order_by('pk')
        for option in options:
            row.append('')

            # add the response time
            row.append(rt)

    else:
        options = question.options.all().order_by('pk')
        for option in options:

            answer = answer_set.answers.filter(question=question, answer_value=option.pk).first()

            if answer:
                answer_val = 1
                rt += answer.reaction_time_ms
            else:
                answer_val = 0

            row.append(answer_val)

            # add the response time
            row.append(rt)

    return row, rt


def append_radio_answers(answer_set, question, row):

    rt = 0

    answer = answer_set.answers.filter(question=question).first()

    if answer:
        answer.link_to_option()
        value = answer.answered_option.value if answer.answered_option else "[ DB ERROR DETECTED ]"
        ascii_value = str(value)
        row.append(ascii_value)
        rt += answer.reaction_time_ms
    else:
        row.append('')

    # add the response time
    row.append(rt)

    return row, rt


def append_slider_answers(answer_set, question, row):

    rt = 0

    answer = answer_set.answers.filter(question=question).first()

    if answer:
        ascii_value = answer.answer_value.encode('ascii', 'ignore').decode('ascii')
        row.append(ascii_value)
        rt += answer.reaction_time_ms
    else:
        row.append('')

    # add the response time
    row.append(rt)

    return row, rt


def send_export_success_email(archive_filename, program, user, timestamp):

    current_site = Site.objects.get_current()

    url = 'http://{}{}'.format(current_site.domain, os.path.join(settings.MEDIA_URL, 'exports', archive_filename))

    context = {
        'download_url': url,
        'program_name': program.editing_version.display_name,
        'first_name': user.first_name,
        'export_timestamp': timestamp
    }

    email = TemplateEmail(template='email/export_complete.html', context=context, to=[user.email], from_email='export@sema-surveys.com')
    email.send()


def get_timestamp_str(answer_set, timezone):

    import arrow

    ts = arrow.get(answer_set).to(timezone)
    return ts.format('DD/MM/YYYY HH:mm:ss')


@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def export_data_for_version(total_count, cur_count, version_id, export_path):

    file_exists = os.path.exists(export_path)

    with open(export_path, 'a') as csv_file:

        version = ProgramVersion.objects.get(pk=version_id)
        program = version.program

        logger.info("Exporting data for {} v{}".format(version.display_name, version.revision_number))

        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        questions = Question.objects.filter(
            set__program_version=version,
        ).order_by('pk').prefetch_related('options')

        gc.disable()

        headers = ['PARTICIPANT_ID', 'ITERATION', 'PROGRAM_VERSION', 'SURVEY', 'HAS_ANSWERS', 'DELIVERED', 'COMPLETED', 'EXPIRED', 'UPLOADED', 'TIMEZONE', 'RESPONSE_TIME_MS']
        headers_append = headers.append

        # Get the insertion point
        response_time_insertion_index = len(headers) - 1

        for question in questions.iterator():

            if question.question_type == Question.QUESTION_TYPE_MULTICHOICE:

                for option in question.options.all().order_by('pk'):
                    title = question.question_tag.upper() + '-' + str(option.value)
                    headers_append(title)
                    headers_append(title + '_RT')
            else:
                headers_append(question.question_tag.upper())
                headers_append(question.question_tag.upper() + '_RT')

            time.sleep(0.1)

        if not file_exists:
            writer.writerow(headers)

        gc.enable()

        version_answer_sets = version.answer_sets.filter(is_duplicate=False).order_by('user__pk', 'pk').prefetch_related('answers')
        paginator = Paginator(version_answer_sets, 1000) # 1000 rows at once

        for page_number in paginator.page_range:
            answer_sets = paginator.page(page_number).object_list

            for answer_set in answer_sets:

                has_answers = "YES" if answer_set.has_answers else "NO"

                timezone = answer_set.timezone
                if not timezone:
                    timezone = 'Australia/Melbourne'

                delivered = get_timestamp_str(answer_set.delivery_timestamp, timezone)

                if answer_set.completed_timestamp:
                    completed = get_timestamp_str(answer_set.completed_timestamp, timezone)
                else:
                    completed = ''

                if answer_set.expiry_timestamp:
                    expired = get_timestamp_str(answer_set.expiry_timestamp, timezone)
                else:
                    expired = ''

                uploaded = get_timestamp_str(answer_set.uploaded_timestamp, timezone)

                gc.disable()

                row = [answer_set.user.username, str(answer_set.iteration), str(version.revision_number), answer_set.survey.display_name, has_answers, delivered, completed, expired, uploaded, timezone, ]

                total_response_time = 0

                for question in questions:

                    rt = 0

                    if question.question_type == Question.QUESTION_TYPE_TEXT:
                        row, rt = append_text_answers(answer_set, question, row)

                    elif question.question_type == Question.QUESTION_TYPE_MULTICHOICE:
                        row, rt = append_multichoice_answers(answer_set, question, row)

                    elif question.question_type == Question.QUESTION_TYPE_RADIO:
                        row, rt = append_radio_answers(answer_set, question, row)

                    elif question.question_type == Question.QUESTION_TYPE_SLIDER:
                        row, rt = append_slider_answers(answer_set, question, row)

                    total_response_time += rt

                # Insert the response time into the row
                row.insert(response_time_insertion_index, total_response_time)

                # Now write the row
                writer.writerow(row)

                gc.enable()

                cur_count += 1

                if cur_count % 100 == 0:
                    program.export_percentage = int((float(cur_count) / float(total_count)) * 100)
                    program.save()

                time.sleep(0.1)

    logger.info("Export complete.")

    return cur_count


@task(name='tasks.export_data')
def export_data(program_id, user_pk, email_on_completion, archive_password):

    program = Program.objects.get(pk=program_id)
    user = User.objects.get(pk=user_pk)

    logger.info("Exporting data for Program {}".format(program.pk))

    timestamp = arrow.utcnow()
    timestamp_str = timestamp.to('Australia/Melbourne').format("YYYY_MM_DD_HH_mm_ss")

    export_root = os.path.join(settings.MEDIA_ROOT, 'exports')

    if not os.path.exists(export_root):
        os.makedirs(export_root)

    with make_temp_directory() as export_tmp_root:

        archive_filename = "sema_export_{}_{}.zip".format(program.editing_version.display_name.replace(' ', '_'), timestamp_str)
        archive_path = os.path.join(export_root, archive_filename)

        z = zipfile.ZipFile(archive_path, "w")

        if archive_password and len(archive_password) > 0:
            z.setpassword(archive_password)

        try:
            total_count = AnswerSet.unique_objects.filter(program_version__program=program).count()
            cur_count = 0
            q = multiprocessing.Queue()

            for version in program.versions.all().order_by('pk').iterator():

                filename = "{}_v{}_{}.csv".format(version.display_name.replace(' ', '_'), version.revision_number, timestamp_str)
                export_path = os.path.join(export_tmp_root, filename)

                # Run each version in a different process to reduce memory usage (memory will be regained after process exit)
                cur_count = export_data_for_version(total_count, cur_count, version.pk, export_path)

                z.write(export_path, filename)

            z.close()

            # Success send an email
            send_export_success_email(archive_filename, program, user, timestamp_str)

            program.export_status = Program.EXPORT_STATUS_COMPLETED_OK
            program.save()

        except Exception, e:
            logger.exception("Error exporting data.")
            program.export_status = Program.EXPORT_STATUS_ERROR
            program.save()

    logger.info("Export completed for Program {}".format(program.pk))

