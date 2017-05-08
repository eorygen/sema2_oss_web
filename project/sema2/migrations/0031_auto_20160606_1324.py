# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0030_programparticipantbridge_is_running_latest_app_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='display_name',
            field=models.TextField(),
        ),
    ]
