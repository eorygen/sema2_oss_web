# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema2', '0033_auto_20160817_0728'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConditionalQuestionSetPredicate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=True)),
                ('target_text', models.TextField()),
                ('target_min_value_incl', models.IntegerField(default=-1)),
                ('target_max_value_incl', models.IntegerField(default=-1)),
                ('question', models.ForeignKey(related_name='predicates', to='sema2.Question')),
                ('target_option', models.ForeignKey(blank=True, to='sema2.QuestionOption', null=True)),
                ('target_question_set', models.ForeignKey(related_name='predicates', blank=True, to='sema2.QuestionSet', null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AlterField(
            model_name='program',
            name='export_status',
            field=models.IntegerField(default=0, choices=[(0, b'Ready'), (1, b'In Progress'), (2, b'Error'), (3, b'Success')]),
        ),
    ]
