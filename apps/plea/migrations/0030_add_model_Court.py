# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Court'
        db.create_table(u'plea_court', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('court_code', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('region_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('court_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('court_address', self.gf('django.db.models.fields.TextField')()),
            ('court_telephone', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('court_email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('submission_email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('plp_email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('test_mode', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'plea', ['Court'])


    def backwards(self, orm):
        # Deleting model 'Court'
        db.delete_table(u'plea_court')


    models = {
        u'plea.case': {
            'Meta': {'object_name': 'Case'},
            'case_number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'forenames': ('django.db.models.fields.CharField', [], {'max_length': '105', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '35', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '35', 'null': 'True', 'blank': 'True'}),
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
        u'plea.court': {
            'Meta': {'object_name': 'Court'},
            'court_address': ('django.db.models.fields.TextField', [], {}),
            'court_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'court_email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'court_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'court_telephone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plp_email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'submission_email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'test_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'total_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_not_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_pleas': ('django.db.models.fields.IntegerField', [], {})
        },
        u'plea.offence': {
            'Meta': {'object_name': 'Offence'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offences'", 'to': u"orm['plea.Case']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offence_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'offence_seq_number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'offence_short_title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'offence_wording': ('django.db.models.fields.TextField', [], {'max_length': '4000'}),
            'ou_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
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