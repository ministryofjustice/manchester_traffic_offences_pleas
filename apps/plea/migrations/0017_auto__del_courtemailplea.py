# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CourtEmailPlea'
        db.delete_table(u'plea_courtemailplea')


    def backwards(self, orm):
        # Adding model 'CourtEmailPlea'
        db.create_table(u'plea_courtemailplea', (
            ('status', self.gf('django.db.models.fields.CharField')(default='not_sent', max_length=30)),
            ('address_from', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('dict_sent', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('body_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('address_to', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('hearing_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('attachment_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('urn', self.gf('django.db.models.fields.CharField')(max_length=16, db_index=True)),
            ('date_sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'plea', ['CourtEmailPlea'])


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
            'total_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_not_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_pleas': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['plea']