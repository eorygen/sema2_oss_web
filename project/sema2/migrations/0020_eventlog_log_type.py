# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0019_auto_20150526_0824'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlog',
            name='log_type',
            field=models.IntegerField(default=0, choices=[(0, b'Note'), (1, b'Note'), (2, b'Note'), (3, b'Note'), (4, b'Note'), (5, b'Note'), (6, b'Note'), (7, b'Note')]),
        ),
    ]
