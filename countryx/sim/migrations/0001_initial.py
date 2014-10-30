# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('term', models.CharField(max_length=20)),
                ('year', models.IntegerField()),
                ('created_date', models.DateTimeField(verbose_name=b'created_date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionAdministrator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section', models.ForeignKey(to='sim.Section')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('section', models.ForeignKey(to='sim.Section')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionGroupPlayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='sim.SectionGroup')),
                ('role', models.ForeignKey(to='sim.Role')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionGroupPlayerTurn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('turn', models.IntegerField()),
                ('choice', models.IntegerField(null=True)),
                ('reasoning', models.TextField(null=True)),
                ('automatic_update', models.IntegerField(default=0)),
                ('submit_date', models.DateTimeField(null=True, verbose_name=b'final date submitted')),
                ('feedback', models.TextField(null=True)),
                ('feedback_date', models.DateTimeField(null=True, verbose_name=b'feedback submitted')),
                ('faculty', models.ForeignKey(related_name='sectiongroupplayerturn_related_faculty', to='sim.SectionAdministrator', null=True)),
                ('player', models.ForeignKey(related_name='sectiongroupplayerturn_related_player', to='sim.SectionGroupPlayer')),
            ],
            options={
                'get_latest_by': 'submit_date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionGroupState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_updated', models.DateTimeField(verbose_name=b'date updated')),
                ('group', models.ForeignKey(to='sim.SectionGroup')),
            ],
            options={
                'get_latest_by': 'date_updated',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionTurnDates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('turn1', models.DateTimeField(verbose_name=b'turn1')),
                ('turn2', models.DateTimeField(null=True, verbose_name=b'turn2')),
                ('turn3', models.DateTimeField(null=True, verbose_name=b'turn3')),
                ('section', models.ForeignKey(to='sim.Section')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('turn', models.IntegerField()),
                ('state_no', models.IntegerField()),
                ('name', models.CharField(max_length=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StateChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('president', models.IntegerField()),
                ('envoy', models.IntegerField()),
                ('regional', models.IntegerField()),
                ('opposition', models.IntegerField()),
                ('next_state', models.ForeignKey(related_name='statechange_related_next', to='sim.State')),
                ('state', models.ForeignKey(related_name='statechange_related_current', to='sim.State')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StateRoleChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.IntegerField()),
                ('desc', models.CharField(max_length=250)),
                ('role', models.ForeignKey(to='sim.Role')),
                ('state', models.ForeignKey(to='sim.State')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StateVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('value', models.TextField()),
                ('state', models.ForeignKey(to='sim.State')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sectiongroupstate',
            name='state',
            field=models.ForeignKey(to='sim.State'),
            preserve_default=True,
        ),
    ]
