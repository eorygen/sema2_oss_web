from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import TemplateView, View, RedirectView
import jwt
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from sema2 import tasks
from sema2.api import ProgramSerializer, ProgramVersionSerializer, AnswerSetSerializer
from sema2.models import Program, ProgramInvite, ProgramParticipantState, ProgramParticipantBridge, AnswerSet
import tokens


class HomeRedirectView(View):

    def get(self, request):

        if request.user.groups.filter(name='sema_admin').exists():
            return HttpResponseRedirect(redirect_to=reverse('program-list'))
        else:
            return HttpResponseRedirect(redirect_to=reverse('home'))


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)
        context['show_welcome'] = self.request.GET.get('welcome', False)
        return context

class ProgramListView(TemplateView):
    template_name = 'program_list.html'


class ProgramRedirectView(View):

    def get(self, request, program_id):
        return HttpResponseRedirect(redirect_to=reverse('dashboard', kwargs={'program_id': program_id}))


class ProgramDashboardView(TemplateView):
    template_name = 'program_dashboard.html'

    def dispatch(self, request, *args, **kwargs):

        user = request.user

        try:
            program = Program.objects.get(pk=kwargs['program_id'])
            is_admin = program.admins.filter(pk=user.pk).exists()

        except Program.DoesNotExist:
            program = None

        if not user.is_authenticated() or not program or not is_admin:
            return HttpResponseRedirect(redirect_to=reverse('program-list'))

        return super(ProgramDashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProgramDashboardView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)
        return context


class ProgramParticipantsView(TemplateView):
    template_name = 'program_participants.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramParticipantsView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)
        return context


class ProgramAdminsView(TemplateView):
    template_name = 'program_admins.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramAdminsView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)
        return context


class ProgramQuestionSetsView(TemplateView):
    template_name = 'program_question_sets.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramQuestionSetsView, self).get_context_data(**kwargs)

        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)
        return context


class ProgramSurveysView(TemplateView):
    template_name = 'program_surveys.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramSurveysView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)
        return context


class ProgramSchedulesView(TemplateView):
    template_name = 'program_schedules.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramSchedulesView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)
        return context


class ProgramResponsesView(TemplateView):
    template_name = 'program_responses.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramResponsesView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)

        context['cur_page'] = self.request.GET.get('p', 1)
        context['sort_by'] = self.request.GET.get('s', '')

        context['filtered_user_id'] = self.request.GET.get('u', -1)

        return context


class ProgramResponseView(TemplateView):
    template_name = 'program_response.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramResponseView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)

        answer_set = AnswerSet.objects.get(pk=kwargs['set_id'])
        context['answer_set_json'] = JSONRenderer().render(AnswerSetSerializer(answer_set).data)

        context['cur_page'] = self.request.GET.get('p', 1)

        return context


class ProgramActivityView(TemplateView):
    template_name = 'program_activity.html'

    def get_context_data(self, **kwargs):
        context = super(ProgramActivityView, self).get_context_data(**kwargs)
        program = Program.objects.get(pk=kwargs['program_id'])
        context['program_json'] = JSONRenderer().render(ProgramSerializer(program).data)

        version = self.request.GET.get('v', None)
        program_version = program.versions.get(revision_number=version) if version else program.versions.all().order_by('-pk').first()
        context['program_version_json'] = JSONRenderer().render(ProgramVersionSerializer(program_version).data)

        return context


class MailTest(APIView):

    def get(self, request):
        invite, token = tasks.generate_confirmation_token(request.GET.get('id'))
        return Response({'token': token})


class MailTest2(APIView):

    def get(self, request):

        # from django.core.mail import send_mail
        # send_mail('Subject here', 'Here is the message.', 'system@boostedhuman.com', ['ashemah@boostedhuman.com'], fail_silently=False)
        # tasks.send_participant_invite(1)
        return Response({})


class ConfirmInvite(View):

    def get(self, request, confirmation_token, *args, **kwargs):

        try:
            payload = jwt.decode(confirmation_token, key=settings.JWT_SECRET)

            invitation_id = payload['invitation_id']

            try:
                # Create a new user from the invite
                invitation = ProgramInvite.objects.get(pk=invitation_id)

                url = tasks.confirm_invite_and_get_welcome_url(invitation)
                invitation.delete()

                return HttpResponseRedirect(redirect_to=url)

            except ProgramInvite.DoesNotExist:
                return HttpResponseRedirect(redirect_to=reverse('home'))

        except jwt.InvalidTokenError:
            return HttpResponse(status=403)


class InitialSetup(View):

    def get(self, request):

        site = Site.objects.all().first()

        if settings.DEBUG:
            site.domain = 'exo:8000'
            site.name = 'Development'
        else:
            site.domain = 'sema-survey.com'
            site.name = 'SEMA'

        site.save()

        from django.contrib.auth.models import Group
        if Group.objects.all().count() == 0:

            Group.objects.create(
               name='sema_participant'
            )

            Group.objects.create(
                name='sema_admin'
            )

        admin = User.objects.get(username='admin')
        g = Group.objects.get(name='sema_admin')
        g.user_set.add(admin)
        admin.save()

        return HttpResponse("Ok")
