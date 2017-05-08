# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0021_auto_20150729_0909'),
    ]

    operations = [
        migrations.RenameField(
            model_name='programinvite',
            old_name='skip_email_confirmation',
            new_name='require_email_confirmation',
        ),
    ]
