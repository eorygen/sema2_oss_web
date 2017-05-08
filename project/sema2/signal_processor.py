import uuid
from sema2 import tasks
from sema2.models import Question, Schedule, ProgramParticipantState, ProgramParticipantBridge, AnswerSet


def process_program_save(sender, instance, **kwargs):

    if kwargs['raw']:
        return

    from models import Program, ProgramVersion, QuestionSet, Survey

    program = instance
    created = kwargs['created']

    # Create a default version for it
    if created:

        new_version = ProgramVersion.objects.create(
            display_name='New Program',
            description='',
            program=program,
            revision_number=1
        )

        program.editing_version = new_version

        # Create the default sub objects
        question_set = QuestionSet.objects.create(
            program_version=new_version,
            display_name='Default Set',
            uuid=str(uuid.uuid4()),
        )

        question = Question.objects.create(
            set=question_set,
            question_type=Question.QUESTION_TYPE_TEXT,
            question_text='Example Text Question',
            question_tag='example',
            uuid=str(uuid.uuid4()),
        )

        schedule = Schedule.objects.create(
            display_name="Default",
            program_version=new_version,
            uuid=str(uuid.uuid4()),
        )

        survey = Survey.objects.create(
            program_version=new_version,
            display_name='Default Questions',
            uuid=str(uuid.uuid4()),
            schedule=schedule
        )

        survey.question_sets.add(question_set)

        program.save()


def process_participant_invite_save(sender, instance, **kwargs):

    if kwargs['raw']:
        return

    if kwargs['created']:
        tasks.send_participant_invite(instance.pk)


def process_answer_set_pre_save(sender, instance, **kwargs):
    pass


def process_conditional_question_set(sender, instance, **kwargs):
    instance.link_to_option()


def process_answer_set_save(sender, instance, **kwargs):

    if kwargs['raw']:
        return

    from tasks import calculate_participant_compliance

    created = kwargs['created']

    if created:

        # See if we already have an instance of this record
        # If so then mark it as a duplicate
        # One of the clients is sending duplicates sometimes
        is_duplicate = AnswerSet.objects.filter(user=instance.user, program_version=instance.program_version, iteration=instance.iteration, completed_timestamp=instance.completed_timestamp).count() > 1
        if is_duplicate:
            instance.is_duplicate = True
            instance.save()

        # Then update the user's program participant state
        state = ProgramParticipantState.get_for_user_and_survey_uuid(instance.user, instance.survey.uuid)

        if instance.iteration > state.current_iteration:
            state.current_iteration = instance.iteration
            state.save()

        #calculate_participant_compliance.apply_async((instance.user.pk, instance.survey.program_version.program.pk,), countdown=5)
