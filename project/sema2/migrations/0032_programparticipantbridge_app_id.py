# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0031_auto_20160606_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='app_id',
            field=models.CharField(default=b'com.orygenapps.sema', max_length=60),
        ),
    ]
