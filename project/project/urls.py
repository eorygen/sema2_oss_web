from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
import boosted_uplink
from sema2.api import ProgramViewSet, SurveyViewSet, QuestionSetViewSet, AnswerSetViewSet, ScheduleViewSet, \
    QuestionViewSet, ProgramInviteViewSet, ParticipantViewSet

router = routers.DefaultRouter()

router.register(r'programs', ProgramViewSet, base_name='programs')
router.register(r'surveys', SurveyViewSet, base_name='surveys')
router.register(r'sets', QuestionSetViewSet, base_name='sets')
router.register(r'questions', QuestionViewSet, base_name='questions')
router.register(r'answers', AnswerSetViewSet, base_name='answers')
router.register(r'schedules', ScheduleViewSet, base_name='schedules')
router.register(r'invitations', ProgramInviteViewSet, base_name='participant-invites')
router.register(r'participants', ParticipantViewSet, base_name='participants')

urlpatterns = patterns('',
    url(r'^', include('sema2.urls')),
    url(r'^api/1/token/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api/1/uplink/', include('boosted_uplink.urls')),
    url(r'^api/1/', include(router.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:

    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
)