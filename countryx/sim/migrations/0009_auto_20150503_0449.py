# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def populate_description(apps, schema_editor):
    StateVariable = apps.get_model('sim', 'StateVariable')
    for sv in StateVariable.objects.filter(name='Country Condition'):
        sv.state.description = sv.value
        sv.state.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0008_auto_20150503_0444'),
    ]

    operations = [
        migrations.RunPython(populate_description),
    ]
