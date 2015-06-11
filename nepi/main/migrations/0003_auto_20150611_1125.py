# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def rename_hierarchies(apps, schema_editor):
    Hierarchy = apps.get_model("pagetree", "Hierarchy")

    try:
        main = Hierarchy.objects.get(name='main')
        main.name = 'optionb-en'
        main.base_url = '/pages/optionb/en/'
        main.save()
    except Hierarchy.DoesNotExist:
        pass

    try:
        fr = Hierarchy.objects.get(name='fr')
        fr.name = 'optionb-fr'
        fr.base_url = '/pages/optionb/fr/'
        fr.save()
    except Hierarchy.DoesNotExist:
        pass

    try:
        pt = Hierarchy.objects.get(name='pt')
        pt.name = 'optionb-pt'
        pt.base_url = '/pages/optionb/pt/'
        pt.save()
    except Hierarchy.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_userprofile_language'),
    ]

    operations = [
        migrations.RunPython(rename_hierarchies),
    ]
