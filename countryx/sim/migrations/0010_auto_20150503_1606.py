# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0009_auto_20150503_0449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staterolechoice',
            name='desc',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
