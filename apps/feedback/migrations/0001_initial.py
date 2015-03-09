# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserRating'
        db.create_table(u'feedback_userrating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('rating', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'feedback', ['UserRating'])

        # Adding model 'UserRatingAggregate'
        db.create_table(u'feedback_userratingaggregate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('feedback_count', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('feedback_total', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('feedback_avg', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'feedback', ['UserRatingAggregate'])


    def backwards(self, orm):
        # Deleting model 'UserRating'
        db.delete_table(u'feedback_userrating')

        # Deleting model 'UserRatingAggregate'
        db.delete_table(u'feedback_userratingaggregate')


    models = {
        u'feedback.userrating': {
            'Meta': {'object_name': 'UserRating'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'feedback.userratingaggregate': {
            'Meta': {'object_name': 'UserRatingAggregate'},
            'feedback_avg': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'feedback_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'feedback_total': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['feedback']