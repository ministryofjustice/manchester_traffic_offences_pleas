# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CourtEmailPlea.status_info'
        db.add_column(u'plea_courtemailplea', 'status_info',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'CourtEmailPlea.dict_sent'
        db.alter_column(u'plea_courtemailplea', 'dict_sent', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CourtEmailPlea.body_text'
        db.alter_column(u'plea_courtemailplea', 'body_text', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CourtEmailPlea.attachment_text'
        db.alter_column(u'plea_courtemailplea', 'attachment_text', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):
        # Deleting field 'CourtEmailPlea.status_info'
        db.delete_column(u'plea_courtemailplea', 'status_info')


        # Changing field 'CourtEmailPlea.dict_sent'
        db.alter_column(u'plea_courtemailplea', 'dict_sent', self.gf('django.db.models.fields.TextField')(default='sent'))

        # Changing field 'CourtEmailPlea.body_text'
        db.alter_column(u'plea_courtemailplea', 'body_text', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'CourtEmailPlea.attachment_text'
        db.alter_column(u'plea_courtemailplea', 'attachment_text', self.gf('django.db.models.fields.TextField')(default=''))

    models = {
        u'plea.courtemailplea': {
            'Meta': {'ordering': "['-date_sent']", 'object_name': 'CourtEmailPlea'},
            'address_from': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'address_to': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'attachment_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dict_sent': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_sent'", 'max_length': '10'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['plea']