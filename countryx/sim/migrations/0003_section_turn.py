# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0002_auto_20150427_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='turn',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
