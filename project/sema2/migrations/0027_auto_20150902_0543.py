# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0026_answerset_is_duplicate'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionset',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'Active'), (1, b'Archived')]),
        ),
        migrations.AlterField(
            model_name='program',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'Active'), (1, b'Archived')]),
        ),
    ]
