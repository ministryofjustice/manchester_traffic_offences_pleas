# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CourtEmailCount'
        db.create_table(u'plea_courtemailcount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('total_pleas', self.gf('django.db.models.fields.IntegerField')()),
            ('total_guilty', self.gf('django.db.models.fields.IntegerField')()),
            ('total_not_guilty', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'plea', ['CourtEmailCount'])


    def backwards(self, orm):
        # Deleting model 'CourtEmailCount'
        db.delete_table(u'plea_courtemailcount')


    models = {
        u'plea.courtemailcount': {
            'Meta': {'object_name': 'CourtEmailCount'},
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_sent'", 'max_length': '30'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['plea']