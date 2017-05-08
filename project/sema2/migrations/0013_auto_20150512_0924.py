# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0012_auto_20150430_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='programparticipantbridge',
            name='compliance_start_timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='questionset',
            name='group',
            field=models.ManyToManyField(related_name='question_sets', null=True, to='sema2.Survey', blank=True),
        ),
    ]
