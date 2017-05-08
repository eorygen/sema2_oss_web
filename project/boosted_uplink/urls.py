from django.conf.urls import url, patterns
from boosted_uplink.views import FeedbackView, AppUpdateView

urlpatterns = patterns('',
    url(r'^feedback/$', FeedbackView.as_view(), name='feedback'),
    url(r'^update/$', AppUpdateView.as_view(), name='update'),)
