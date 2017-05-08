from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required, user_passes_test
from sema2.api import SyncView, TestPushView, UpdateStatisticsView
from sema2.views import ProgramParticipantsView, ProgramQuestionSetsView, ProgramListView, \
    ProgramRedirectView, ProgramAdminsView, ProgramSchedulesView, ProgramResponsesView, ProgramSurveysView, \
    HomeRedirectView, MailTest, ConfirmInvite, HomeView, ProgramDashboardView, InitialSetup, ProgramResponseView, \
    ProgramActivityView, MailTest2


def is_admin_member(user):
    is_admin = user.groups.filter(name='sema_admin').exists() or user.is_staff
    return is_admin

urlpatterns = patterns('',

    url(r'^api/1/sync/$', SyncView.as_view(), name='sync'),
    url(r'^api/1/pushtest/', TestPushView.as_view(), name='pushtest'),
    url(r'^api/1/updatestats/', UpdateStatisticsView.as_view(), name='updatestats'),

    url(r'^setup/$', InitialSetup.as_view(), name='initial-setup'),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^$', HomeRedirectView.as_view(), name='index'),
    url(r'^home/$',  HomeView.as_view(template_name='home.html'), name='home'),
    url(r'^programs/$', user_passes_test(is_admin_member)(ProgramListView.as_view()), name='program-list'),
    url(r'^programs/(?P<program_id>\d+)/$', user_passes_test(is_admin_member)(ProgramRedirectView.as_view()), name='redirect'),
    url(r'^programs/(?P<program_id>\d+)/dashboard/$', user_passes_test(is_admin_member)(ProgramDashboardView.as_view()), name='dashboard'),
    url(r'^programs/(?P<program_id>\d+)/participants/$', user_passes_test(is_admin_member)(ProgramParticipantsView.as_view()), name='participants'),
    url(r'^programs/(?P<program_id>\d+)/admins/$', user_passes_test(is_admin_member)(ProgramAdminsView.as_view()), name='admins'),
    url(r'^programs/(?P<program_id>\d+)/questions/$', user_passes_test(is_admin_member)(ProgramQuestionSetsView.as_view()), name='questions'),
    url(r'^programs/(?P<program_id>\d+)/surveys/$', user_passes_test(is_admin_member)(ProgramSurveysView.as_view()), name='surveys'),
    url(r'^programs/(?P<program_id>\d+)/schedules/$', user_passes_test(is_admin_member)(ProgramSchedulesView.as_view()), name='schedules'),
    url(r'^programs/(?P<program_id>\d+)/activity/$', user_passes_test(is_admin_member)(ProgramActivityView.as_view()), name='activity'),
    url(r'^programs/(?P<program_id>\d+)/responses/(?P<set_id>\d+)/$', user_passes_test(is_admin_member)(ProgramResponseView.as_view()), name='response'),
    url(r'^programs/(?P<program_id>\d+)/responses/$', user_passes_test(is_admin_member)(ProgramResponsesView.as_view()), name='responses'),

    url(r'^join/(?P<confirmation_token>.+)/$', ConfirmInvite.as_view(), name='confirm-invite'),

    url(r'^test001/$', MailTest.as_view(), name='mail-test'),
    url(r'^test002/$', MailTest2.as_view(), name='mail-test2'),
)