# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NurseConversation'
        db.create_table(u'activities_nurseconversation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dialog_one', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('dialog_two', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal(u'activities', ['NurseConversation'])

        # Adding model 'PatientConversation'
        db.create_table(u'activities_patientconversation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dialog_one', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('dialog_two', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal(u'activities', ['PatientConversation'])

        # Adding model 'ConversationDialog'
        db.create_table(u'activities_conversationdialog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'activities', ['ConversationDialog'])

        # Adding model 'ConversationScenario'
        db.create_table(u'activities_conversationscenario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('starting_party', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('nurse_bubbles', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.NurseConversation'])),
            ('patient_bubbles', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.PatientConversation'])),
            ('dialog', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.ConversationDialog'])),
        ))
        db.send_create_signal(u'activities', ['ConversationScenario'])

        # Adding model 'Conversation'
        db.create_table(u'activities_conversation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('good_conversation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='good_conversation', null=True, to=orm['activities.ConversationScenario'])),
            ('bad_conversation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bad_conversation', null=True, to=orm['activities.ConversationScenario'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'activities', ['Conversation'])

        # Adding model 'ConversationResponse'
        db.create_table(u'activities_conversationresponse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('conversation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Conversation'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('submitted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('first_click', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('second_selection', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'activities', ['ConversationResponse'])


    def backwards(self, orm):
        # Deleting model 'NurseConversation'
        db.delete_table(u'activities_nurseconversation')

        # Deleting model 'PatientConversation'
        db.delete_table(u'activities_patientconversation')

        # Deleting model 'ConversationDialog'
        db.delete_table(u'activities_conversationdialog')

        # Deleting model 'ConversationScenario'
        db.delete_table(u'activities_conversationscenario')

        # Deleting model 'Conversation'
        db.delete_table(u'activities_conversation')

        # Deleting model 'ConversationResponse'
        db.delete_table(u'activities_conversationresponse')


    models = {
        u'activities.conversation': {
            'Meta': {'object_name': 'Conversation'},
            'bad_conversation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bad_conversation'", 'null': 'True', 'to': u"orm['activities.ConversationScenario']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'good_conversation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'good_conversation'", 'null': 'True', 'to': u"orm['activities.ConversationScenario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.conversationdialog': {
            'Meta': {'object_name': 'ConversationDialog'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'activities.conversationresponse': {
            'Meta': {'object_name': 'ConversationResponse'},
            'conversation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Conversation']"}),
            'first_click': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'second_selection': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'activities.conversationscenario': {
            'Meta': {'object_name': 'ConversationScenario'},
            'dialog': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.ConversationDialog']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nurse_bubbles': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.NurseConversation']"}),
            'patient_bubbles': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.PatientConversation']"}),
            'starting_party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        u'activities.nurseconversation': {
            'Meta': {'object_name': 'NurseConversation'},
            'dialog_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'dialog_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.patientconversation': {
            'Meta': {'object_name': 'PatientConversation'},
            'dialog_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'dialog_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pagetree.hierarchy': {
            'Meta': {'object_name': 'Hierarchy'},
            'base_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'pagetree.pageblock': {
            'Meta': {'ordering': "('section', 'ordinality')", 'object_name': 'PageBlock'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'css_extra': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ordinality': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pagetree.Section']"})
        },
        u'pagetree.section': {
            'Meta': {'object_name': 'Section'},
            'deep_toc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'hierarchy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pagetree.Hierarchy']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show_toc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['activities']