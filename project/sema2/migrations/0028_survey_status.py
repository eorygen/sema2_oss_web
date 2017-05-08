# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0027_auto_20150902_0543'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'Active'), (1, b'Archived')]),
        ),
    ]
