# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CaseAction'
        db.create_table(u'plea_caseaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['plea.Case'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'plea', ['CaseAction'])

        # Adding field 'CourtEmailCount.sent'
        db.add_column(u'plea_courtemailcount', 'sent',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'CourtEmailCount.processed'
        db.add_column(u'plea_courtemailcount', 'processed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Case.sent'
        db.add_column(u'plea_case', 'sent',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Case.processed'
        db.add_column(u'plea_case', 'processed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'CaseAction'
        db.delete_table(u'plea_caseaction')

        # Deleting field 'CourtEmailCount.sent'
        db.delete_column(u'plea_courtemailcount', 'sent')

        # Deleting field 'CourtEmailCount.processed'
        db.delete_column(u'plea_courtemailcount', 'processed')

        # Deleting field 'Case.sent'
        db.delete_column(u'plea_case', 'sent')

        # Deleting field 'Case.processed'
        db.delete_column(u'plea_case', 'processed')


    models = {
        u'plea.case': {
            'Meta': {'object_name': 'Case'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'created_not_sent'", 'max_length': '30'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'urn': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'})
        },
        u'plea.caseaction': {
            'Meta': {'object_name': 'CaseAction'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': u"orm['plea.Case']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'plea.courtemailcount': {
            'Meta': {'object_name': 'CourtEmailCount'},
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hearing_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sc_guilty_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'sc_not_guilty_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_not_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_pleas': ('django.db.models.fields.IntegerField', [], {})
        },
        u'plea.usagestats': {
            'Meta': {'ordering': "('start_date',)", 'object_name': 'UsageStats'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'online_guilty_pleas': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'online_not_guilty_pleas': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'online_submissions': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'postal_requisitions': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'postal_responses': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['plea']