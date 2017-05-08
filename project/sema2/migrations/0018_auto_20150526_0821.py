# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sema2', '0017_programparticipantbridge_cached_last_sync_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlog',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 26, 8, 21, 55, 917329, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventlog',
            name='user',
            field=models.ForeignKey(related_name='events', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
