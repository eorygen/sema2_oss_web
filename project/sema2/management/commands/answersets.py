import arrow
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from sema2.models import AnswerSet, ProgramParticipantBridge, Program, Survey, EventLog


class Command(BaseCommand):

    help = 'Management Tools'

    def add_arguments(self, parser):
        parser.add_argument('--survey_id', type=int)
        parser.add_argument('--program_id', type=int)
        parser.add_argument('--participant_id', type=int)
        parser.add_argument('--answered', action='store_true')
        parser.add_argument('--dryrun', action='store_true')

        parser.add_argument('--cmd',
                    type=str,
                    default='list')

    def handle(self, *args, **options):

        self.stdout.write('Running command...')

        cmd = options['cmd']

        dry_run = options['dryrun']

        if dry_run:
            print "IS DRY RUN"

        if cmd == 'list':
            self.stdout.write('listing answersets')

            program_id = options['program_id']
            participant_id = options['participant_id']
            survey_id = options['survey_id']
            is_answered_only = options['answered']

            sets = AnswerSet.objects.filter(program_version__program=program_id, survey=survey_id, user__username=participant_id).order_by('created_timestamp')

            for set in sets:

                if set.has_answers or not is_answered_only:
                    print set

        # elif cmd == 'delete-empty-rows':
        #
        #     self.stdout.write('deleting empty answersets')
        #
        #     program_id = options['program_id']
        #     participant_id = options['participant_id']
        #     survey_id = options['survey_id']
        #
        #     sets = AnswerSet.objects.filter(program_version__program=program_id, survey=survey_id, user__username=participant_id).order_by('created_timestamp')
        #
        #     for set in sets:
        #
        #         if not set.has_answers:
        #             print set
        #
        #             if not dry_run:
        #                 set.delete()

        elif cmd == 'renumber-iterations':

            self.stdout.write('renumbering iterations')

            program_id = options['program_id']
            participant_id = options['participant_id']
            survey_id = options['survey_id']

            sets = AnswerSet.objects.filter(program_version__program=program_id, survey=survey_id, user__username=participant_id).order_by('created_timestamp')

            iteration = 1

            for set in sets:

                set.iteration = iteration
                print set

                if not dry_run:
                    set.save()

                iteration += 1

        elif cmd == 'list-programs':

            self.stdout.write('Listing programs')
            self.stdout.write('-')

            programs = Program.objects.filter(log_type__in=[EventLog.LOG_PROGRAM_EDIT, EventLog.LOG_PROGRAM_PUBLISH]).order_by('timestamp')

            for program in programs:
                print "{} - {}".format(program.pk, program.editing_version.display_name)

        elif cmd == 'list-program-edits':

            self.stdout.write('Listing program edits')
            self.stdout.write('-')

            logs = EventLog.objects.filter(log_type__in=[EventLog.LOG_PROGRAM_EDIT, EventLog.LOG_PROGRAM_PUBLISH]).order_by('timestamp')

            for log in logs:
                local_time = arrow.get(log.timestamp, 'utc').to('australia/melbourne')
                print "{} - {} - {} - {}".format(local_time, log.program_version.display_name, log, log.user.email)

        elif cmd == 'check-program':

            program_id = options['program_id']
            program = Program.objects.get(pk=program_id)

            self.stdout.write('Checking program {}'.format(program.editing_version.display_name))

            participant_id = options['participant_id'] if 'participant_id' in options else None

            if participant_id:
                participants = program.participants.filter(username=participant_id)
            else:
                participants = program.participants.all().exclude(username__in=['0778331', '0926011', '3315798', '3867614', '8073412', 'admin', '9987154'])

            uuids = Survey.objects.filter(program_version__program=program_id).values_list('uuid', flat=True).distinct()
            print uuids

            missing_peeps = []
            largest_gap = 0

            for participant in participants:

                bridge = ProgramParticipantBridge.objects.get(user=participant, program=program_id)

                self.stdout.write('PARTICIPANT: {} - {} - {}'.format(participant, participant.email, bridge.app_platform_name))

                for uuid in uuids:

                    uuid = str(uuid)

                    # self.stdout.write('-')
                    # self.stdout.write('SURVEY: {}'.format(uuid))
                    # self.stdout.write('-')

                    sets = AnswerSet.objects.filter(program_version__program=program_id, survey__uuid=uuid, user__username=participant.username).order_by('delivery_timestamp')

                    count = 0
                    duplicates = 0
                    missing = 0

                    last_date = None
                    last_iteration = -1
                    iteration = sets[0].iteration if len(sets) > 0 else 0

                    for set in sets:

                        print "ITERATION {}".format(set.iteration)

                        if set.iteration == last_iteration:
                            print "SKIPPING DUPLICATE ITERATION {}".format(last_iteration)
                            duplicates += 1
                        else:

                            # print "EXPECTED {} --> {}".format(iteration, set.iteration)

                            if iteration != set.iteration:

                                interval = (set.iteration - iteration)

                                last_date_local = arrow.get(last_date, 'utc').to('australia/melbourne').format('HH:mm:ss DD/MM/YYYY')
                                date_local = arrow.get(set.delivery_timestamp, 'utc').to('australia/melbourne').format('HH:mm:ss DD/MM/YYYY')
                                interval_time = set.delivery_timestamp - last_date
                                is_scary = interval_time > timedelta(hours=4)
                                interval_str = str(interval_time)

                                # if interval > 0:
                                #     print "MISSING {} ITERATION(s): {} -> {}, GAP: {} -> {}, {} - > {}".format(interval, iteration, set.iteration, last_date_local, date_local, interval_str, is_scary)
                                # else:
                                #     print "TIMEWARP {} ITERATION(s): {} -> {}, GAP: {} -> {}, {}".format(interval, iteration, set.iteration, last_date_local, date_local, interval_str)

                                iteration = set.iteration

                                missing += interval

                                if missing > largest_gap:
                                    largest_gap = missing

                            last_iteration = iteration

                            iteration += 1

                        count += 1
                        last_date = set.delivery_timestamp

                    print "\n-\nTOTAL {}, DUPES {}, MISSING {}\n--".format(count, duplicates, missing)

                    if missing > 0:
                        missing_peeps.append({
                            'user': participant.username,
                            'count': missing,
                            'platform': bridge.app_platform_name,
                            'joined': participant.date_joined
                        })

            from operator import itemgetter
            sorted_peeps = sorted(missing_peeps, key=itemgetter('count'))

            print 'MISSING PEEPS:'

            for peep in sorted_peeps:
                peep['joined'] = arrow.get(peep['joined']).format('DD/MM/YYYY')
                print ":{}".format(peep)

            print 'LARGEST GAP {}'.format(largest_gap)

        elif cmd == 'remove-dupes':

            program_id = options['program_id']
            program = Program.objects.get(pk=program_id)

            self.stdout.write('Checking program {}'.format(program.editing_version.display_name))

            participant_id = options['participant_id'] if 'participant_id' in options else None

            if participant_id:
                participants = program.participants.filter(username=participant_id)
            else:
                participants = program.participants.all().exclude(username__in=['0778331', '0926011', '3315798', '3867614', '8073412', 'admin', '9987154'])

            uuids = Survey.objects.filter(program_version__program=program_id).values_list('uuid', flat=True).distinct()
            print uuids

            total_dupes = 0

            for participant in participants:

                bridge = ProgramParticipantBridge.objects.get(user=participant, program=program_id)

                self.stdout.write('PARTICIPANT: {} - {} - {}'.format(participant, participant.email, bridge.app_platform_name))

                for uuid in uuids:

                    uuid = str(uuid)

                    sets = AnswerSet.objects.filter(program_version__program=program_id, survey__uuid=uuid, user__username=participant.username, is_duplicate=False).order_by('delivery_timestamp')

                    count = 0
                    duplicates = 0
                    missing = 0

                    last_iteration = -1
                    iteration = sets[0].iteration if len(sets) > 0 else 0

                    for set in sets:

                        # print "ITERATION {}".format(set.iteration)

                        if set.iteration == last_iteration:

                            if not dry_run:
                                set.is_duplicate = True
                                set.save()
                                print "[SAVE] SKIPPING DUPLICATE ITERATION {}".format(last_iteration)
                            else:
                                print "SKIPPING DUPLICATE ITERATION {}".format(last_iteration)

                            duplicates += 1
                        else:

                            last_iteration = iteration
                            iteration += 1

                        count += 1

                    print "\n-\nTOTAL {}, DUPES {}, MISSING {}\n--".format(count, duplicates, missing)
                    total_dupes += duplicates

            print "\n-\nTOTAL DUPES {}\n--".format(total_dupes)

        self.stdout.write('Done.')
