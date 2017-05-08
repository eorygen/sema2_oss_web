# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sema2', '0011_answer_answered_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='export_completion_timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='program',
            name='export_initiator_user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='export_percentage',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='program',
            name='export_status',
            field=models.IntegerField(default=0, choices=[(0, b'Ready'), (1, b'In Progress'), (2, b'Error')]),
        ),
        migrations.AlterField(
            model_name='programparticipantbridge',
            name='program_participant_status',
            field=models.IntegerField(default=0, choices=[(0, b'Active'), (1, b'Stopped'), (2, b'Archived')]),
        ),
    ]
