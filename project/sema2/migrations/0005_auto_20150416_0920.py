# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0004_programparticipantbridge_force_data_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='cached_answered_answer_set_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='cached_compliance_fraction',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='cached_received_answer_set_count',
            field=models.IntegerField(default=0),
        ),
    ]
