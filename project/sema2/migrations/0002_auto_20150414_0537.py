# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='programparticipantbridge',
            name='status',
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='program_participant_status',
            field=models.IntegerField(default=0, choices=[(0, b'Active'), (1, b'Disabled'), (2, b'Archived')]),
        ),
    ]
