# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0002_auto_20150414_0537'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='custom_start_hour',
            field=models.IntegerField(default=9),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='custom_start_minute',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='custom_stop_hour',
            field=models.IntegerField(default=17),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='custom_stop_minute',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='programparticipantbridge',
            name='use_custom_start_stop_time',
            field=models.BooleanField(default=False),
        ),
    ]
