# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-18 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_auto_20150918_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convclick',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='retentionclick',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
