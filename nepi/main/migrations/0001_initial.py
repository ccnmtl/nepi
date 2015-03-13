# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pagetree', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateQuizScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quiz_class', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=2)),
                ('display_name', models.TextField()),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('name', models.CharField(max_length=50)),
                ('archived', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(related_name='created_by', to=settings.AUTH_USER_MODEL)),
                ('module', models.ForeignKey(default=None, blank=True, to='pagetree.Hierarchy', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PendingTeachers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('country', models.ForeignKey(to='main.Country')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile_type', models.CharField(max_length=2, choices=[(b'ST', b'Student'), (b'TE', b'Teacher'), (b'IN', b'Institution'), (b'CA', b'Country Administrator'), (b'IC', b'ICAP')])),
                ('icap_affil', models.BooleanField(default=False)),
                ('country', models.ForeignKey(to='main.Country')),
                ('group', models.ManyToManyField(default=None, to='main.Group', null=True, blank=True)),
                ('school', models.ForeignKey(default=None, blank=True, to='main.School', null=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='school',
            unique_together=set([('name', 'country')]),
        ),
        migrations.AddField(
            model_name='pendingteachers',
            name='school',
            field=models.ForeignKey(to='main.School'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pendingteachers',
            name='user_profile',
            field=models.ForeignKey(related_name='pending_teachers', to='main.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='school',
            field=models.ForeignKey(to='main.School'),
            preserve_default=True,
        ),
    ]
