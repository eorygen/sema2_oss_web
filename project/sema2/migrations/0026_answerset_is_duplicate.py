# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0025_program_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerset',
            name='is_duplicate',
            field=models.BooleanField(default=False),
        ),
    ]
