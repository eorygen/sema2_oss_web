# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0022_auto_20150810_0145'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='cached_last_sync_interval_seconds',
            field=models.IntegerField(default=-1),
        ),
    ]
