# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0010_auto_20150421_0420'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='answered_option',
            field=models.ForeignKey(blank=True, to='sema2.QuestionOption', null=True),
        ),
    ]
