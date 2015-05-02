# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations
import json


def populate_statechange_roles(apps, schema_editor):
    StateChange = apps.get_model("sim", "StateChange")
    for s in StateChange.objects.all():
        d = {
            'President': s.president,
            'FirstWorldEnvoy': s.envoy,
            'SubRegionalRep': s.regional,
            'OppositionLeadership': s.opposition,
        }
        s.roles = json.dumps(d)
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0005_statechange_roles'),
    ]

    operations = [
        migrations.RunPython(populate_statechange_roles)
    ]
