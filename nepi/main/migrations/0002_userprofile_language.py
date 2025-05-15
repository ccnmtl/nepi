# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default=b'en', max_length=255,
                                   choices=[(b'en', 'English'),
                                            (b'fr', 'French'),
                                            (b'pt', 'Portuguese')]),
            preserve_default=True,
        ),
    ]
