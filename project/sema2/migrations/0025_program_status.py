# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0024_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
