# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0020_eventlog_log_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='cached_compliance_fraction',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='program',
            name='cached_longest_sync_interval_participant_id_list',
            field=jsonfield.fields.JSONField(default=[]),
        ),
        migrations.AddField(
            model_name='program',
            name='cached_top_compliance_participant_id_list',
            field=jsonfield.fields.JSONField(default=[]),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='log_type',
            field=models.IntegerField(default=0, choices=[(0, b'Note'), (1, b'Sync'), (2, b'Data Upload'), (3, b'App Upgrade'), (4, b'Program Edit'), (5, b'Program Publish'), (6, b'Data Export'), (7, b'User State Change')]),
        ),
    ]
