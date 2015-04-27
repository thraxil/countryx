# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='term',
        ),
        migrations.RemoveField(
            model_name='section',
            name='year',
        ),
    ]
