# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0003_section_turn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sectionturndates',
            name='section',
        ),
        migrations.DeleteModel(
            name='SectionTurnDates',
        ),
    ]
