# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'UsageStats.submissions'
        db.delete_column(u'plea_usagestats', 'submissions')

        # Deleting field 'UsageStats.requisitions'
        db.delete_column(u'plea_usagestats', 'requisitions')

        # Adding field 'UsageStats.online_submissions'
        db.add_column(u'plea_usagestats', 'online_submissions',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'UsageStats.postal_requisitions'
        db.add_column(u'plea_usagestats', 'postal_requisitions',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'UsageStats.postal_responses'
        db.add_column(u'plea_usagestats', 'postal_responses',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'UsageStats.submissions'
        db.add_column(u'plea_usagestats', 'submissions',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'UsageStats.requisitions'
        db.add_column(u'plea_usagestats', 'requisitions',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'UsageStats.online_submissions'
        db.delete_column(u'plea_usagestats', 'online_submissions')

        # Deleting field 'UsageStats.postal_requisitions'
        db.delete_column(u'plea_usagestats', 'postal_requisitions')

        # Deleting field 'UsageStats.postal_responses'
        db.delete_column(u'plea_usagestats', 'postal_responses')


    models = {
        u'plea.case': {
            'Meta': {'object_name': 'Case'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'created_not_sent'", 'max_length': '30'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'urn': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'})
        },
        u'plea.courtemailcount': {
            'Meta': {'object_name': 'CourtEmailCount'},
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hearing_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sc_guilty_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'sc_not_guilty_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_not_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_pleas': ('django.db.models.fields.IntegerField', [], {})
        },
        u'plea.usagestats': {
            'Meta': {'ordering': "('start_date',)", 'object_name': 'UsageStats'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'online_submissions': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'postal_requisitions': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'postal_responses': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['plea']