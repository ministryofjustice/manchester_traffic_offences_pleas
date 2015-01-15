# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """
        Copy urn/status and status_info from CourtEmailPlea to the new
        Case table.
        """

        for plea in orm.CourtEmailPlea.objects.all():
            orm.Case.objects.create(urn=plea.urn,
                                    status=plea.status,
                                    status_info=plea.status)

    def backwards(self, orm):
        "Write your backwards methods here."

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
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'urn': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'})
        }
    }

    complete_apps = ['plea']
    symmetrical = True
