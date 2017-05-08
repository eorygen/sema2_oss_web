# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0009_auto_20150420_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerset',
            name='completed_timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
