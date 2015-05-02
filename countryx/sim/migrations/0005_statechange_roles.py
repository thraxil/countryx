# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0004_auto_20150428_0639'),
    ]

    operations = [
        migrations.AddField(
            model_name='statechange',
            name='roles',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
