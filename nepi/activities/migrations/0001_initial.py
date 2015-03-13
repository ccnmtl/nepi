# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdherenceCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quiz_class', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ARTCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intro_text', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalendarChart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(default=b'')),
                ('correct_date', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalendarResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('calendar_activity', models.ForeignKey(blank=True, to='activities.CalendarChart', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConvClick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scenario_type', models.CharField(default=b'G', max_length=1, choices=[(b'G', b'Good'), (b'B', b'Bad')])),
                ('text_one', models.CharField(max_length=255, null=True, blank=True)),
                ('response_one', models.CharField(max_length=255, null=True, blank=True)),
                ('response_two', models.CharField(max_length=255, null=True, blank=True)),
                ('response_three', models.CharField(max_length=255, null=True, blank=True)),
                ('complete_dialog', models.TextField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConversationResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConversationScenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(blank=True)),
                ('bad_conversation', models.ForeignKey(related_name='bad_conversation', blank=True, to='activities.Conversation', null=True)),
                ('good_conversation', models.ForeignKey(related_name='good_conversation', blank=True, to='activities.Conversation', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(default=1)),
                ('explanation', models.TextField(default=b'')),
            ],
            options={
                'ordering': ['number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DosageActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('explanation', models.TextField()),
                ('question', models.TextField()),
                ('ml_nvp', models.DecimalField(default=0.0, max_digits=4, decimal_places=2)),
                ('times_day', models.IntegerField(default=0)),
                ('weeks', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DosageActivityResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ml_nvp', models.DecimalField(default=0.0, max_digits=4, decimal_places=2)),
                ('times_day', models.IntegerField()),
                ('weeks', models.IntegerField()),
                ('dosage_activity', models.ForeignKey(related_name='dosage_resp', blank=True, to='activities.DosageActivity', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageInteractive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intro_text', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(default=b'', max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RetentionClick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('click_string', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RetentionRateCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intro_text', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RetentionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cohort_click', models.ForeignKey(related_name='retention_cohort_click', blank=True, to='activities.RetentionClick', null=True)),
                ('delivery_date_click', models.ForeignKey(related_name='retention_delivery_date_click', blank=True, to='activities.RetentionClick', null=True)),
                ('eligible_click', models.ForeignKey(related_name='retention_eligible_click', blank=True, to='activities.RetentionClick', null=True)),
                ('follow_up_click', models.ForeignKey(related_name='retention_follow_up_click', blank=True, to='activities.RetentionClick', null=True)),
                ('retentionrate', models.ForeignKey(blank=True, to='activities.RetentionRateCard', null=True)),
                ('start_date_click', models.ForeignKey(related_name='retention_start_date_click', blank=True, to='activities.RetentionClick', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='day',
            name='calendar',
            field=models.ForeignKey(to='activities.Month'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conversationresponse',
            name='conv_scen',
            field=models.ForeignKey(blank=True, to='activities.ConversationScenario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conversationresponse',
            name='first_click',
            field=models.ForeignKey(related_name='first_click', blank=True, to='activities.ConvClick', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conversationresponse',
            name='second_click',
            field=models.ForeignKey(related_name='second_click', blank=True, to='activities.ConvClick', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conversationresponse',
            name='third_click',
            field=models.ForeignKey(related_name='third_click', blank=True, to='activities.ConvClick', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conversationresponse',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='convclick',
            name='conversation',
            field=models.ForeignKey(blank=True, to='activities.Conversation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendarresponse',
            name='correct_click',
            field=models.ForeignKey(related_name='correct_click', blank=True, to='activities.Day', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendarresponse',
            name='first_click',
            field=models.ForeignKey(related_name='first_click', blank=True, to='activities.Day', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendarresponse',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendarchart',
            name='month',
            field=models.ForeignKey(to='activities.Month'),
            preserve_default=True,
        ),
    ]
