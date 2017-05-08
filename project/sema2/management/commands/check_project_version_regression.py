from django.core.management.base import BaseCommand, CommandError
from sema2.models import AnswerSet, ProgramParticipantBridge, Program, Survey, EventLog


class Command(BaseCommand):

    help = 'Check project version regression'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        self.stdout.write('Checking for project version regression')

        programs = Program.objects.all()

        for program in programs:

            version_numbers = set()
            last_version = None

            for version in program.versions.all().order_by('pk'):

                if version.revision_number in version_numbers:
                    # self.stdout.write('REVERSION IN {} {}: Revision {}, Version PK {}'.format(program.active_version.display_name, program.pk, version.revision_number, version.pk))

                    if last_version:
                        if last_version.answer_sets.count() > 0:
                            self.stdout.write('{} {} - POTENTIAL OVERWRITE OF REVISION {} BY REVISION {}'.format(program.active_version.display_name, program.pk, last_version.revision_number, version.revision_number))
                else:
                    version_numbers.add(version.revision_number)

                last_version = version

        self.stdout.write('Check complete.')
