# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0005_auto_20150416_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='app_version_number',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='app_version_string',
            field=models.CharField(default=b'1.0.0', max_length=20),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='device_push_token',
            field=models.TextField(null=True, blank=True),
        ),
    ]
