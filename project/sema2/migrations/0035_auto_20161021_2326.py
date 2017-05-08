# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0034_auto_20161020_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conditionalquestionsetpredicate',
            name='target_text',
        ),
        migrations.AddField(
            model_name='conditionalquestionsetpredicate',
            name='target_value',
            field=models.TextField(null=True, blank=True),
        ),
    ]
