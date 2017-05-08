# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0036_conditionalquestionsetpredicate_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='feature_enable_conditional_question_sets',
            field=models.BooleanField(default=False),
        ),
    ]
