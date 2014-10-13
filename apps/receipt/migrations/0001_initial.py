# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReceiptLog'
        db.create_table(u'receipt_receiptlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('run_time', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('query_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('query_to', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('total_emails', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('total_errors', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('total_failed', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('status_detail', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'receipt', ['ReceiptLog'])


    def backwards(self, orm):
        # Deleting model 'ReceiptLog'
        db.delete_table(u'receipt_receiptlog')


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
            'total_failed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['receipt']