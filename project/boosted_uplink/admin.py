from django.contrib import admin
from boosted_uplink.models import FeedbackItem, AppUpdateConfig, UplinkConfig

admin.site.register(UplinkConfig)
admin.site.register(FeedbackItem)
admin.site.register(AppUpdateConfig)