# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'DosageActivity.question'
        db.alter_column(u'activities_dosageactivity', 'question', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):

        # Changing field 'DosageActivity.question'
        db.alter_column(u'activities_dosageactivity', 'question', self.gf('django.db.models.fields.CharField')(max_length=64))

    models = {
        u'activities.adherencecard': {
            'Meta': {'object_name': 'AdherenceCard'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'quiz_class': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'activities.artcard': {
            'Meta': {'object_name': 'ARTCard'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_text': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'activities.calendarchart': {
            'Meta': {'object_name': 'CalendarChart'},
            'correct_date': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Month']"})
        },
        u'activities.calendarresponse': {
            'Meta': {'object_name': 'CalendarResponse'},
            'conv_scen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.CalendarChart']", 'null': 'True', 'blank': 'True'}),
            'first_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_first_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_last_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'activities.convclick': {
            'Meta': {'object_name': 'ConvClick'},
            'conversation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Conversation']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.conversation': {
            'Meta': {'object_name': 'Conversation'},
            'complete_dialog': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'response_three': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'response_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'scenario_type': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'}),
            'text_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'activities.conversationresponse': {
            'Meta': {'object_name': 'ConversationResponse'},
            'conv_scen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.ConversationScenario']", 'null': 'True', 'blank': 'True'}),
            'first_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'first_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'second_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'second_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'third_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'third_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'activities.conversationscenario': {
            'Meta': {'object_name': 'ConversationScenario'},
            'bad_conversation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bad_conversation'", 'null': 'True', 'to': u"orm['activities.Conversation']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'good_conversation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'good_conversation'", 'null': 'True', 'to': u"orm['activities.Conversation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.day': {
            'Meta': {'object_name': 'Day'},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Month']"}),
            'explanation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'activities.dosageactivity': {
            'Meta': {'object_name': 'DosageActivity'},
            'explanation': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ml_nvp': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.TextField', [], {}),
            'times_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weeks': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'activities.dosageactivityresponse': {
            'Meta': {'object_name': 'DosageActivityResponse'},
            'dosage_activity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'dosage_resp'", 'null': 'True', 'to': u"orm['activities.DosageActivity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ml_nvp': ('django.db.models.fields.IntegerField', [], {}),
            'times_day': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'weeks': ('django.db.models.fields.IntegerField', [], {})
        },
        u'activities.imageinteractive': {
            'Meta': {'object_name': 'ImageInteractive'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_text': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'activities.month': {
            'Meta': {'object_name': 'Month'},
            'display_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.retentionclick': {
            'Meta': {'object_name': 'RetentionClick'},
            'click_string': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.retentionratecard': {
            'Meta': {'object_name': 'RetentionRateCard'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_text': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'activities.retentionresponse': {
            'Meta': {'object_name': 'RetentionResponse'},
            'apr_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_apr_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'cohort_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_cohort_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'dec_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_dec_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'delivery_date_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_delivery_date_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'eligible_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_eligible_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'feb_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_feb_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jan_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_jan_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'jun_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_jun_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'mar_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_mar_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'may_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_may_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'retentionrate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.RetentionRateCard']", 'null': 'True', 'blank': 'True'}),
            'start_date_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'retention_start_date_click'", 'null': 'True', 'to': u"orm['activities.RetentionClick']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
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