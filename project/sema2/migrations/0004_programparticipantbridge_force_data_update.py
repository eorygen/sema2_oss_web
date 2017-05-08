# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0003_auto_20150414_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='force_data_update',
            field=models.BooleanField(default=False),
        ),
    ]
