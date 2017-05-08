# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0014_auto_20150512_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='reaction_time_ms',
            field=models.IntegerField(default=0),
        ),
    ]
