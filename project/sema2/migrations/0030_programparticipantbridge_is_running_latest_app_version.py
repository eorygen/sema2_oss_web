# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0029_auto_20160408_0204'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='is_running_latest_app_version',
            field=models.BooleanField(default=False),
        ),
    ]
