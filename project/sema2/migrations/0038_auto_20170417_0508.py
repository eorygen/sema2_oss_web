# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0037_program_feature_enable_conditional_question_sets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='display_name',
            field=models.CharField(max_length=60),
        ),
    ]
