# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django.db.models.deletion
from django.conf import settings
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer_value', models.TextField()),
                ('answered_timestamp', models.DateTimeField()),
                ('displayed_timestamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='AnswerSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', uuidfield.fields.UUIDField(max_length=32)),
                ('iteration', models.IntegerField()),
                ('created_timestamp', models.DateTimeField()),
                ('delivery_timestamp', models.DateTimeField()),
                ('expiry_timestamp', models.DateTimeField()),
                ('completed_timestamp', models.DateTimeField()),
                ('uploaded_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('data', jsonfield.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=False)),
                ('contact_name', models.CharField(max_length=120)),
                ('contact_email', models.CharField(max_length=120)),
                ('contact_phone_number', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invitation_type', models.IntegerField(default=0)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('email_address', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20, null=True, blank=True)),
                ('welcome_message', models.TextField(default=b'', blank=True)),
                ('is_existing_user', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=20, null=True, blank=True)),
                ('password', models.CharField(max_length=32, null=True, blank=True)),
                ('sent_timestamp', models.DateTimeField(auto_now_add=True)),
                ('inviting_user', models.ForeignKey(related_name='invitations', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(related_name='invitations', to='sema2.Program')),
            ],
        ),
        migrations.CreateModel(
            name='ProgramParticipantBridge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=True)),
                ('program', models.ForeignKey(related_name='program_profiles', to='sema2.Program')),
                ('user', models.ForeignKey(related_name='program_profiles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramParticipantState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('survey_uuid', models.UUIDField()),
                ('current_iteration', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(related_name='participant_states', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('editing_status', models.IntegerField(default=0, choices=[(0, b'Draft'), (1, b'Published')])),
                ('display_name', models.CharField(max_length=80)),
                ('description', models.TextField(null=True, blank=True)),
                ('revision_number', models.IntegerField()),
                ('program', models.ForeignKey(related_name='versions', to='sema2.Program')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', uuidfield.fields.UUIDField(max_length=32)),
                ('randomise_option_order', models.BooleanField(default=False)),
                ('question_type', models.IntegerField(default=0, choices=[(0, b'Text'), (1, b'Mutichoice'), (2, b'Radio'), (3, b'Slider')])),
                ('question_text', models.CharField(max_length=255)),
                ('question_tag', models.CharField(max_length=60)),
                ('min_value', models.IntegerField(default=1)),
                ('min_label', models.CharField(default=b'Min', max_length=255)),
                ('max_value', models.IntegerField(default=5)),
                ('max_label', models.CharField(default=b'Max', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255)),
                ('value', models.IntegerField(default=-1)),
                ('question', models.ForeignKey(related_name='options', to='sema2.Question')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(max_length=60)),
                ('randomise_question_order', models.BooleanField(default=False)),
                ('uuid', uuidfield.fields.UUIDField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', uuidfield.fields.UUIDField(max_length=32)),
                ('display_name', models.CharField(max_length=20)),
                ('interval_minutes', models.IntegerField(default=120)),
                ('expiry_minutes', models.IntegerField(default=120)),
                ('start_time_hours', models.IntegerField(default=9)),
                ('start_time_minutes', models.IntegerField(default=0)),
                ('stop_time_hours', models.IntegerField(default=17)),
                ('stop_time_minutes', models.IntegerField(default=0)),
                ('offset_plus_minus_minutes', models.IntegerField(default=0)),
                ('allow_monday', models.BooleanField(default=True)),
                ('allow_tuesday', models.BooleanField(default=True)),
                ('allow_wednesday', models.BooleanField(default=True)),
                ('allow_thursday', models.BooleanField(default=True)),
                ('allow_friday', models.BooleanField(default=True)),
                ('allow_saturday', models.BooleanField(default=True)),
                ('allow_sunday', models.BooleanField(default=True)),
                ('program_version', models.ForeignKey(related_name='schedules', to='sema2.ProgramVersion')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(max_length=60)),
                ('randomise_set_order', models.BooleanField(default=False)),
                ('trigger_mode', models.IntegerField(default=0, choices=[(0, b'Scheduled'), (1, b'Adhoc')])),
                ('max_iterations', models.IntegerField(default=-1)),
                ('uuid', uuidfield.fields.UUIDField(max_length=32)),
                ('participants', models.ManyToManyField(related_name='surveys', to=settings.AUTH_USER_MODEL)),
                ('program_version', models.ForeignKey(related_name='surveys', to='sema2.ProgramVersion')),
                ('schedule', models.ForeignKey(related_name='surveys', blank=True, to='sema2.Schedule', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='questionset',
            name='group',
            field=models.ManyToManyField(related_name='question_sets', to='sema2.Survey'),
        ),
        migrations.AddField(
            model_name='questionset',
            name='program_version',
            field=models.ForeignKey(related_name='question_sets', to='sema2.ProgramVersion'),
        ),
        migrations.AddField(
            model_name='question',
            name='set',
            field=models.ForeignKey(related_name='questions', to='sema2.QuestionSet'),
        ),
        migrations.AddField(
            model_name='program',
            name='active_version',
            field=models.OneToOneField(related_name='parent', null=True, blank=True, to='sema2.ProgramVersion'),
        ),
        migrations.AddField(
            model_name='program',
            name='admins',
            field=models.ManyToManyField(related_name='administered_programs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='program',
            name='editing_version',
            field=models.OneToOneField(related_name='editing_parent', null=True, blank=True, to='sema2.ProgramVersion'),
        ),
        migrations.AddField(
            model_name='program',
            name='participants',
            field=models.ManyToManyField(related_name='participated_programs', through='sema2.ProgramParticipantBridge', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='program_version',
            field=models.ForeignKey(related_name='events', to='sema2.ProgramVersion'),
        ),
        migrations.AddField(
            model_name='answerset',
            name='program_version',
            field=models.ForeignKey(related_name='answer_sets', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sema2.ProgramVersion', null=True),
        ),
        migrations.AddField(
            model_name='answerset',
            name='survey',
            field=models.ForeignKey(related_name='answer_sets', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sema2.Survey', null=True),
        ),
        migrations.AddField(
            model_name='answerset',
            name='user',
            field=models.ForeignKey(related_name='answer_sets', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(related_name='answer', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sema2.Question', null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='set',
            field=models.ForeignKey(related_name='answers', to='sema2.AnswerSet'),
        ),
    ]
