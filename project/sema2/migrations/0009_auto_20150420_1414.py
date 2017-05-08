# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0008_auto_20150420_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programparticipantbridge',
            name='app_platform_name',
            field=models.CharField(default=b'unknown', max_length=10),
        ),
    ]
