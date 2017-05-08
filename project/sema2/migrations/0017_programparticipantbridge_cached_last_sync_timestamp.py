# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0016_programparticipantbridge_cached_last_upload_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='cached_last_sync_timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
