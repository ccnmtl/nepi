# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'NurseConversation'
        db.delete_table(u'activities_nurseconversation')

        # Deleting model 'PatientConversation'
        db.delete_table(u'activities_patientconversation')

        # Deleting model 'ConversationDialog'
        db.delete_table(u'activities_conversationdialog')

        # Deleting field 'ConversationResponse.second_selection'
        db.delete_column(u'activities_conversationresponse', 'second_selection')

        # Deleting field 'ConversationResponse.first_click'
        db.delete_column(u'activities_conversationresponse', 'first_click')


        # Changing field 'ConversationResponse.conversation'
        db.alter_column(u'activities_conversationresponse', 'conversation_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.ConversationScenario']))
        # Deleting field 'Conversation.bad_conversation'
        db.delete_column(u'activities_conversation', 'bad_conversation_id')

        # Deleting field 'Conversation.description'
        db.delete_column(u'activities_conversation', 'description')

        # Deleting field 'Conversation.good_conversation'
        db.delete_column(u'activities_conversation', 'good_conversation_id')

        # Adding field 'Conversation.scenario'
        db.add_column(u'activities_conversation', 'scenario',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.ConversationScenario'], null=True),
                      keep_default=False)

        # Adding field 'Conversation.text_one'
        db.add_column(u'activities_conversation', 'text_one',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'Conversation.text_two'
        db.add_column(u'activities_conversation', 'text_two',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'Conversation.text_three'
        db.add_column(u'activities_conversation', 'text_three',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'Conversation.complete_dialog'
        db.add_column(u'activities_conversation', 'complete_dialog',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Deleting field 'ConversationScenario.starting_party'
        db.delete_column(u'activities_conversationscenario', 'starting_party')

        # Deleting field 'ConversationScenario.patient_bubbles'
        db.delete_column(u'activities_conversationscenario', 'patient_bubbles_id')

        # Deleting field 'ConversationScenario.nurse_bubbles'
        db.delete_column(u'activities_conversationscenario', 'nurse_bubbles_id')

        # Deleting field 'ConversationScenario.dialog'
        db.delete_column(u'activities_conversationscenario', 'dialog_id')

        # Adding field 'ConversationScenario.description'
        db.add_column(u'activities_conversationscenario', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'NurseConversation'
        db.create_table(u'activities_nurseconversation', (
            ('dialog_two', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dialog_one', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal(u'activities', ['NurseConversation'])

        # Adding model 'PatientConversation'
        db.create_table(u'activities_patientconversation', (
            ('dialog_two', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dialog_one', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal(u'activities', ['PatientConversation'])

        # Adding model 'ConversationDialog'
        db.create_table(u'activities_conversationdialog', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'activities', ['ConversationDialog'])

        # Adding field 'ConversationResponse.second_selection'
        db.add_column(u'activities_conversationresponse', 'second_selection',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ConversationResponse.first_click'
        db.add_column(u'activities_conversationresponse', 'first_click',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True),
                      keep_default=False)


        # Changing field 'ConversationResponse.conversation'
        db.alter_column(u'activities_conversationresponse', 'conversation_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Conversation']))
        # Adding field 'Conversation.bad_conversation'
        db.add_column(u'activities_conversation', 'bad_conversation',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='bad_conversation', null=True, to=orm['activities.ConversationScenario']),
                      keep_default=False)

        # Adding field 'Conversation.description'
        db.add_column(u'activities_conversation', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Conversation.good_conversation'
        db.add_column(u'activities_conversation', 'good_conversation',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='good_conversation', null=True, to=orm['activities.ConversationScenario']),
                      keep_default=False)

        # Deleting field 'Conversation.scenario'
        db.delete_column(u'activities_conversation', 'scenario_id')

        # Deleting field 'Conversation.text_one'
        db.delete_column(u'activities_conversation', 'text_one')

        # Deleting field 'Conversation.text_two'
        db.delete_column(u'activities_conversation', 'text_two')

        # Deleting field 'Conversation.text_three'
        db.delete_column(u'activities_conversation', 'text_three')

        # Deleting field 'Conversation.complete_dialog'
        db.delete_column(u'activities_conversation', 'complete_dialog')

        # Adding field 'ConversationScenario.starting_party'
        db.add_column(u'activities_conversationscenario', 'starting_party',
                      self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'ConversationScenario.patient_bubbles'
        raise RuntimeError("Cannot reverse this migration. 'ConversationScenario.patient_bubbles' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ConversationScenario.nurse_bubbles'
        raise RuntimeError("Cannot reverse this migration. 'ConversationScenario.nurse_bubbles' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ConversationScenario.dialog'
        raise RuntimeError("Cannot reverse this migration. 'ConversationScenario.dialog' and its values cannot be restored.")
        # Deleting field 'ConversationScenario.description'
        db.delete_column(u'activities_conversationscenario', 'description')


    models = {
        u'activities.conversation': {
            'Meta': {'object_name': 'Conversation'},
            'complete_dialog': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.ConversationScenario']", 'null': 'True'}),
            'text_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'text_three': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'text_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        u'activities.conversationresponse': {
            'Meta': {'object_name': 'ConversationResponse'},
            'conversation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.ConversationScenario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'activities.conversationscenario': {
            'Meta': {'object_name': 'ConversationScenario'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
