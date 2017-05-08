# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0035_auto_20161021_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='conditionalquestionsetpredicate',
            name='action',
            field=models.IntegerField(default=0),
        ),
    ]
