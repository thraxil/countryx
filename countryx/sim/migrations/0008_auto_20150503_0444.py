# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0007_auto_20150502_0549'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='state',
            options={'ordering': ['turn', 'state_no']},
        ),
        migrations.AlterModelOptions(
            name='staterolechoice',
            options={'ordering': ['state', 'role', 'choice']},
        ),
        migrations.AddField(
            model_name='state',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
