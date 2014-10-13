# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ReceiptLog.total_success'
        db.add_column(u'receipt_receiptlog', 'total_success',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ReceiptLog.total_success'
        db.delete_column(u'receipt_receiptlog', 'total_success')


    models = {
        u'receipt.receiptlog': {
            'Meta': {'object_name': 'ReceiptLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'query_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'run_time': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status_detail': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_emails': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'total_errors': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'total_failed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'total_success': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['receipt']