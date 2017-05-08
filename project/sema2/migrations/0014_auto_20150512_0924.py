# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0013_auto_20150512_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionset',
            name='group',
            field=models.ManyToManyField(related_name='question_sets', to='sema2.Survey', blank=True),
        ),
    ]
