# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_auto_20150625_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='response_one',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='response_three',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='response_two',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='text_one',
            field=models.TextField(null=True, blank=True),
        ),
    ]
