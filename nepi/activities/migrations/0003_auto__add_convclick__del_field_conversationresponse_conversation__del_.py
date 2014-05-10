# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ConvClick'
        db.create_table(u'activities_convclick', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('conversation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Conversation'], null=True, blank=True)),
        ))
        db.send_create_signal(u'activities', ['ConvClick'])

        # Deleting field 'ConversationResponse.conversation'
        db.delete_column(u'activities_conversationresponse', 'conversation_id')

        # Deleting field 'ConversationResponse.submitted'
        db.delete_column(u'activities_conversationresponse', 'submitted')

        # Adding field 'ConversationResponse.conv_scen'
        db.add_column(u'activities_conversationresponse', 'conv_scen',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.ConversationScenario'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'ConversationResponse.first_click'
        db.add_column(u'activities_conversationresponse', 'first_click',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='first_click', null=True, to=orm['activities.ConvClick']),
                      keep_default=False)

        # Adding field 'ConversationResponse.second_click'
        db.add_column(u'activities_conversationresponse', 'second_click',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='second_click', null=True, to=orm['activities.ConvClick']),
                      keep_default=False)

        # Adding field 'ConversationResponse.last_click'
        db.add_column(u'activities_conversationresponse', 'last_click',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='third_click', null=True, to=orm['activities.ConvClick']),
                      keep_default=False)


        # Changing field 'ConversationResponse.user'
        db.alter_column(u'activities_conversationresponse', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))
        # Adding field 'Conversation.conversation_type'
        db.add_column(u'activities_conversation', 'conversation_type',
                      self.gf('django.db.models.fields.CharField')(default='G', max_length=1, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ConvClick'
        db.delete_table(u'activities_convclick')


        # User chose to not deal with backwards NULL issues for 'ConversationResponse.conversation'
        raise RuntimeError("Cannot reverse this migration. 'ConversationResponse.conversation' and its values cannot be restored.")
        # Adding field 'ConversationResponse.submitted'
        db.add_column(u'activities_conversationresponse', 'submitted',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Deleting field 'ConversationResponse.conv_scen'
        db.delete_column(u'activities_conversationresponse', 'conv_scen_id')

        # Deleting field 'ConversationResponse.first_click'
        db.delete_column(u'activities_conversationresponse', 'first_click_id')

        # Deleting field 'ConversationResponse.second_click'
        db.delete_column(u'activities_conversationresponse', 'second_click_id')

        # Deleting field 'ConversationResponse.last_click'
        db.delete_column(u'activities_conversationresponse', 'last_click_id')


        # User chose to not deal with backwards NULL issues for 'ConversationResponse.user'
        raise RuntimeError("Cannot reverse this migration. 'ConversationResponse.user' and its values cannot be restored.")
        # Deleting field 'Conversation.conversation_type'
        db.delete_column(u'activities_conversation', 'conversation_type')


    models = {
        u'activities.convclick': {
            'Meta': {'object_name': 'ConvClick'},
            'conversation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Conversation']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.conversation': {
            'Meta': {'object_name': 'Conversation'},
            'complete_dialog': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'conversation_type': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conversations'", 'null': 'True', 'to': u"orm['activities.ConversationScenario']"}),
            'text_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'text_three': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'text_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        u'activities.conversationresponse': {
            'Meta': {'object_name': 'ConversationResponse'},
            'conv_scen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.ConversationScenario']", 'null': 'True', 'blank': 'True'}),
            'first_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'first_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'third_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'second_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'second_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
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
