# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0015_answer_reaction_time_ms'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='cached_last_upload_timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
