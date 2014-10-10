# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CourtEmailCount.sc_guilty_char_count'
        db.add_column(u'plea_courtemailcount', 'sc_guilty_char_count',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'CourtEmailCount.sc_not_guilty_char_count'
        db.add_column(u'plea_courtemailcount', 'sc_not_guilty_char_count',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'CourtEmailCount.national_insurance_char_count'
        db.add_column(u'plea_courtemailcount', 'national_insurance_char_count',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'CourtEmailCount.driving_licence_char_count'
        db.add_column(u'plea_courtemailcount', 'driving_licence_char_count',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'CourtEmailCount.registration_char_count'
        db.add_column(u'plea_courtemailcount', 'registration_char_count',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CourtEmailCount.sc_guilty_char_count'
        db.delete_column(u'plea_courtemailcount', 'sc_guilty_char_count')

        # Deleting field 'CourtEmailCount.sc_not_guilty_char_count'
        db.delete_column(u'plea_courtemailcount', 'sc_not_guilty_char_count')

        # Deleting field 'CourtEmailCount.national_insurance_char_count'
        db.delete_column(u'plea_courtemailcount', 'national_insurance_char_count')

        # Deleting field 'CourtEmailCount.driving_licence_char_count'
        db.delete_column(u'plea_courtemailcount', 'driving_licence_char_count')

        # Deleting field 'CourtEmailCount.registration_char_count'
        db.delete_column(u'plea_courtemailcount', 'registration_char_count')


    models = {
        u'plea.courtemailcount': {
            'Meta': {'object_name': 'CourtEmailCount'},
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'driving_licence_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'hearing_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'national_insurance_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'registration_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'sc_guilty_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'sc_not_guilty_char_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'total_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_not_guilty': ('django.db.models.fields.IntegerField', [], {}),
            'total_pleas': ('django.db.models.fields.IntegerField', [], {})
        },
        u'plea.courtemailplea': {
            'Meta': {'ordering': "['-date_sent']", 'object_name': 'CourtEmailPlea'},
            'address_from': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'address_to': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'attachment_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dict_sent': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hearing_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_sent'", 'max_length': '30'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['plea']