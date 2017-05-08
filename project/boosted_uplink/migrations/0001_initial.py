# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AppUpdateConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('update_url', models.CharField(max_length=255)),
                ('platform_id', models.CharField(max_length=20)),
                ('build_number', models.IntegerField()),
                ('enable_updates', models.BooleanField(default=True)),
                ('changes_text', models.TextField(default=b'', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeedbackItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('category_name', models.CharField(default=b'General', max_length=60)),
                ('priority', models.IntegerField(default=0)),
                ('description', models.TextField()),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UplinkConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enable_app_updates', models.BooleanField(default=True)),
                ('enable_user_feedback', models.BooleanField(default=True)),
            ],
        ),
    ]
