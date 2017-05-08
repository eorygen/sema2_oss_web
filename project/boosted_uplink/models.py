from django.contrib.auth.models import User
from django.db import models


class UplinkConfig(models.Model):

    enable_app_updates = models.BooleanField(default=True)
    enable_user_feedback = models.BooleanField(default=True)

    @classmethod
    def get_uplink_config(self):

        try:
            config = UplinkConfig.objects.first()
        except Exception:
            config = UplinkConfig()
            config.save()

        return config


class FeedbackItem(models.Model):

    PRIORITY_LOW = 0
    PRIORITY_MED = 1
    PRIORITY_HIGH = 2
    PRIORITY_CRITICAL = 3

    user = models.ForeignKey(User, null=True, blank=True)
    user_email = models.EmailField(null=True, blank=True)
    category_name = models.CharField(max_length=60, default="General")
    priority = models.IntegerField(default=PRIORITY_LOW)
    description = models.TextField()


class AppUpdateConfig(models.Model):

    update_url = models.CharField(max_length=255)
    platform_id = models.CharField(max_length=20)
    build_number = models.IntegerField()
    version_name = models.CharField(max_length=10, default="")
    enable_updates = models.BooleanField(default=True)
    changes_text = models.TextField(default="", blank=True, null=True)

    def __unicode__(self):
        return "{} - Build {}".format(self.version_name, self.build_number)