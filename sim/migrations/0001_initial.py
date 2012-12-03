# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Role'
        db.create_table('sim_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sim', ['Role'])

        # Adding model 'State'
        db.create_table('sim_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('turn', self.gf('django.db.models.fields.IntegerField')()),
            ('state_no', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('sim', ['State'])

        # Adding model 'StateChange'
        db.create_table('sim_statechange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(related_name='statechange_related_current', to=orm['sim.State'])),
            ('president', self.gf('django.db.models.fields.IntegerField')()),
            ('envoy', self.gf('django.db.models.fields.IntegerField')()),
            ('regional', self.gf('django.db.models.fields.IntegerField')()),
            ('opposition', self.gf('django.db.models.fields.IntegerField')()),
            ('next_state', self.gf('django.db.models.fields.related.ForeignKey')(related_name='statechange_related_next', to=orm['sim.State'])),
        ))
        db.send_create_signal('sim', ['StateChange'])

        # Adding model 'StateVariable'
        db.create_table('sim_statevariable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.State'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sim', ['StateVariable'])

        # Adding model 'StateRoleChoice'
        db.create_table('sim_staterolechoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.State'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.Role'])),
            ('choice', self.gf('django.db.models.fields.IntegerField')()),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('sim', ['StateRoleChoice'])

        # Adding model 'Section'
        db.create_table('sim_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('sim', ['Section'])

        # Adding model 'SectionAdministrator'
        db.create_table('sim_sectionadministrator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.Section'])),
        ))
        db.send_create_signal('sim', ['SectionAdministrator'])

        # Adding model 'SectionTurnDates'
        db.create_table('sim_sectionturndates', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.Section'])),
            ('turn1', self.gf('django.db.models.fields.DateTimeField')()),
            ('turn2', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('turn3', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('sim', ['SectionTurnDates'])

        # Adding model 'SectionGroup'
        db.create_table('sim_sectiongroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.Section'])),
        ))
        db.send_create_signal('sim', ['SectionGroup'])

        # Adding model 'SectionGroupState'
        db.create_table('sim_sectiongroupstate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.State'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.SectionGroup'])),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('sim', ['SectionGroupState'])

        # Adding model 'SectionGroupPlayer'
        db.create_table('sim_sectiongroupplayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.SectionGroup'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sim.Role'])),
        ))
        db.send_create_signal('sim', ['SectionGroupPlayer'])

        # Adding model 'SectionGroupPlayerTurn'
        db.create_table('sim_sectiongroupplayerturn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sectiongroupplayerturn_related_player', to=orm['sim.SectionGroupPlayer'])),
            ('turn', self.gf('django.db.models.fields.IntegerField')()),
            ('choice', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('reasoning', self.gf('django.db.models.fields.TextField')(null=True)),
            ('automatic_update', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('feedback', self.gf('django.db.models.fields.TextField')(null=True)),
            ('faculty', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sectiongroupplayerturn_related_faculty', null=True, to=orm['sim.SectionAdministrator'])),
            ('feedback_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('sim', ['SectionGroupPlayerTurn'])


    def backwards(self, orm):
        # Deleting model 'Role'
        db.delete_table('sim_role')

        # Deleting model 'State'
        db.delete_table('sim_state')

        # Deleting model 'StateChange'
        db.delete_table('sim_statechange')

        # Deleting model 'StateVariable'
        db.delete_table('sim_statevariable')

        # Deleting model 'StateRoleChoice'
        db.delete_table('sim_staterolechoice')

        # Deleting model 'Section'
        db.delete_table('sim_section')

        # Deleting model 'SectionAdministrator'
        db.delete_table('sim_sectionadministrator')

        # Deleting model 'SectionTurnDates'
        db.delete_table('sim_sectionturndates')

        # Deleting model 'SectionGroup'
        db.delete_table('sim_sectiongroup')

        # Deleting model 'SectionGroupState'
        db.delete_table('sim_sectiongroupstate')

        # Deleting model 'SectionGroupPlayer'
        db.delete_table('sim_sectiongroupplayer')

        # Deleting model 'SectionGroupPlayerTurn'
        db.delete_table('sim_sectiongroupplayerturn')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sim.role': {
            'Meta': {'object_name': 'Role'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'sim.section': {
            'Meta': {'object_name': 'Section'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'sim.sectionadministrator': {
            'Meta': {'object_name': 'SectionAdministrator'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Section']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sim.sectiongroup': {
            'Meta': {'object_name': 'SectionGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Section']"})
        },
        'sim.sectiongroupplayer': {
            'Meta': {'object_name': 'SectionGroupPlayer'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.SectionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sim.sectiongroupplayerturn': {
            'Meta': {'object_name': 'SectionGroupPlayerTurn'},
            'automatic_update': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'choice': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'faculty': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sectiongroupplayerturn_related_faculty'", 'null': 'True', 'to': "orm['sim.SectionAdministrator']"}),
            'feedback': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'feedback_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sectiongroupplayerturn_related_player'", 'to': "orm['sim.SectionGroupPlayer']"}),
            'reasoning': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'turn': ('django.db.models.fields.IntegerField', [], {})
        },
        'sim.sectiongroupstate': {
            'Meta': {'object_name': 'SectionGroupState'},
            'date_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.SectionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.State']"})
        },
        'sim.sectionturndates': {
            'Meta': {'object_name': 'SectionTurnDates'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Section']"}),
            'turn1': ('django.db.models.fields.DateTimeField', [], {}),
            'turn2': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'turn3': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'sim.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'state_no': ('django.db.models.fields.IntegerField', [], {}),
            'turn': ('django.db.models.fields.IntegerField', [], {})
        },
        'sim.statechange': {
            'Meta': {'object_name': 'StateChange'},
            'envoy': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statechange_related_next'", 'to': "orm['sim.State']"}),
            'opposition': ('django.db.models.fields.IntegerField', [], {}),
            'president': ('django.db.models.fields.IntegerField', [], {}),
            'regional': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statechange_related_current'", 'to': "orm['sim.State']"})
        },
        'sim.staterolechoice': {
            'Meta': {'object_name': 'StateRoleChoice'},
            'choice': ('django.db.models.fields.IntegerField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Role']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.State']"})
        },
        'sim.statevariable': {
            'Meta': {'object_name': 'StateVariable'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.State']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['sim']
