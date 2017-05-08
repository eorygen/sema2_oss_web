# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0018_auto_20150526_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlog',
            name='data',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
