# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0006_auto_20150420_0626'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='app_platform_name',
            field=models.CharField(default=b'?', max_length=10),
        ),
    ]
