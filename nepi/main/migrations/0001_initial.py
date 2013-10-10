# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LearningModule'
        db.create_table('main_learningmodule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('main', ['LearningModule'])


    def backwards(self, orm):
        # Deleting model 'LearningModule'
        db.delete_table('main_learningmodule')


    models = {
        'main.learningmodule': {
            'Meta': {'object_name': 'LearningModule'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['main']