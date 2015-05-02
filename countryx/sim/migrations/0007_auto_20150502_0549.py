# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0006_auto_20150502_0434'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statechange',
            name='envoy',
        ),
        migrations.RemoveField(
            model_name='statechange',
            name='opposition',
        ),
        migrations.RemoveField(
            model_name='statechange',
            name='president',
        ),
        migrations.RemoveField(
            model_name='statechange',
            name='regional',
        ),
    ]
