# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0021_auto_20150810_0123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='cached_longest_sync_interval_participant_id_list',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='program',
            name='cached_top_compliance_participant_id_list',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
