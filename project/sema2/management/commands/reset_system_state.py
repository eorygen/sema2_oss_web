from django.core.management.base import BaseCommand, CommandError
from sema2.models import AnswerSet, ProgramParticipantBridge, Program, Survey, EventLog


class Command(BaseCommand):

    help = 'Reset the state of the system after an update (triggered by the deploy script)'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        self.stdout.write('Resetting all program export statuses...')

        programs = Program.objects.all()

        for program in programs:
            program.export_percentage = 0
            program.export_status = Program.EXPORT_STATUS_READY
            program.save()

        self.stdout.write('Reset complete.')
