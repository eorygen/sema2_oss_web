# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0028_survey_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventlog',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='questionoption',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='questionset',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='schedule',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['id']},
        ),
    ]
