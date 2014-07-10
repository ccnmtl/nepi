# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Course'
        db.delete_table(u'main_course')

        # Adding model 'Group'
        db.create_table(u'main_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['main.School'], null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='created_by', null=True, blank=True, to=orm['auth.User'])),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['pagetree.Hierarchy'], null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Group'])

        # Removing M2M table for field course on 'UserProfile'
        db.delete_table(db.shorten_name(u'main_userprofile_course'))

        # Adding M2M table for field group on 'UserProfile'
        m2m_table_name = db.shorten_name(u'main_userprofile_group')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'main.userprofile'], null=False)),
            ('group', models.ForeignKey(orm[u'main.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'group_id'])


    def backwards(self, orm):
        # Adding model 'Course'
        db.create_table(u'main_course', (
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['main.School'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='created_by', null=True, to=orm['auth.User'], blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['pagetree.Hierarchy'], null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'main', ['Course'])

        # Deleting model 'Group'
        db.delete_table(u'main_group')

        # Adding M2M table for field course on 'UserProfile'
        m2m_table_name = db.shorten_name(u'main_userprofile_course')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'main.userprofile'], null=False)),
            ('course', models.ForeignKey(orm[u'main.course'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'course_id'])

        # Removing M2M table for field group on 'UserProfile'
        db.delete_table(db.shorten_name(u'main_userprofile_group'))


    models = {
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
        u'main.country': {
            'Meta': {'object_name': 'Country'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'})
        },
        u'main.group': {
            'Meta': {'object_name': 'Group'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'created_by'", 'null': 'True', 'blank': 'True', 'to': u"orm['auth.User']"}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['pagetree.Hierarchy']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.School']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'main.pendingteachers': {
            'Meta': {'object_name': 'PendingTeachers'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.School']", 'null': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pending_teachers'", 'to': u"orm['main.UserProfile']"})
        },
        u'main.school': {
            'Meta': {'object_name': 'School'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.Country']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'main.userprofile': {
            'Meta': {'ordering': "['user']", 'object_name': 'UserProfile'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.Country']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['main.Group']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'icap_affil': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.School']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'application_user'", 'to': u"orm['auth.User']"})
        },
        u'pagetree.hierarchy': {
            'Meta': {'object_name': 'Hierarchy'},
            'base_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['main']