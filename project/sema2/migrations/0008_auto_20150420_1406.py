# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0007_programparticipantbridge_app_platform_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerset',
            name='timezone',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='timezone',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
    ]
