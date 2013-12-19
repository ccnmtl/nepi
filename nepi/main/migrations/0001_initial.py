# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserVisit'
        db.create_table(u'main_uservisit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pagetree.Section'])),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['UserVisit'])

        # Adding model 'Country'
        db.create_table(u'main_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'main', ['Country'])

        # Adding model 'School'
        db.create_table(u'main_school', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['main.Country'], blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
        ))
        db.send_create_signal(u'main', ['School'])

        # Adding model 'LearningModule'
        db.create_table(u'main_learningmodule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
        ))
        db.send_create_signal(u'main', ['LearningModule'])

        # Adding model 'Course'
        db.create_table(u'main_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['main.School'], blank=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.LearningModule'], blank=True)),
            ('semester', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'main', ['Course'])

        # Adding model 'UserProfile'
        db.create_table(u'main_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='application_user', to=orm['auth.User'])),
            ('profile_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Country'], blank=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['main.School'], null=True)),
        ))
        db.send_create_signal(u'main', ['UserProfile'])

        # Adding M2M table for field visits on 'UserProfile'
        m2m_table_name = db.shorten_name(u'main_userprofile_visits')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'main.userprofile'], null=False)),
            ('uservisit', models.ForeignKey(orm[u'main.uservisit'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'uservisit_id'])

        # Adding M2M table for field course on 'UserProfile'
        m2m_table_name = db.shorten_name(u'main_userprofile_course')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'main.userprofile'], null=False)),
            ('course', models.ForeignKey(orm[u'main.course'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'course_id'])

        # Adding model 'PendingRegister'
        db.create_table(u'main_pendingregister', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.School'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.UserProfile'], null=True, blank=True)),
            ('course', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('profile_type', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
        ))
        db.send_create_signal(u'main', ['PendingRegister'])


    def backwards(self, orm):
        # Deleting model 'UserVisit'
        db.delete_table(u'main_uservisit')

        # Deleting model 'Country'
        db.delete_table(u'main_country')

        # Deleting model 'School'
        db.delete_table(u'main_school')

        # Deleting model 'LearningModule'
        db.delete_table(u'main_learningmodule')

        # Deleting model 'Course'
        db.delete_table(u'main_course')

        # Deleting model 'UserProfile'
        db.delete_table(u'main_userprofile')

        # Removing M2M table for field visits on 'UserProfile'
        db.delete_table(db.shorten_name(u'main_userprofile_visits'))

        # Removing M2M table for field course on 'UserProfile'
        db.delete_table(db.shorten_name(u'main_userprofile_course'))

        # Deleting model 'PendingRegister'
        db.delete_table(u'main_pendingregister')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'main.course': {
            'Meta': {'object_name': 'Course'},
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.LearningModule']", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.School']", 'blank': 'True'}),
            'semester': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'main.learningmodule': {
            'Meta': {'object_name': 'LearningModule'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'})
        },
        u'main.pendingregister': {
            'Meta': {'object_name': 'PendingRegister'},
            'course': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile_type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.School']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.UserProfile']", 'null': 'True', 'blank': 'True'})
        },
        u'main.school': {
            'Meta': {'object_name': 'School'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.Country']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'main.userprofile': {
            'Meta': {'ordering': "['user']", 'object_name': 'UserProfile'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Country']", 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Course']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['main.School']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'application_user'", 'to': u"orm['auth.User']"}),
            'visits': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.UserVisit']", 'null': 'True', 'blank': 'True'})
        },
        u'main.uservisit': {
            'Meta': {'object_name': 'UserVisit'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pagetree.Section']"})
        },
        u'pagetree.hierarchy': {
            'Meta': {'object_name': 'Hierarchy'},
            'base_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
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

    complete_apps = ['main']
