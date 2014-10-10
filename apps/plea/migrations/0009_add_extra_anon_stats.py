# -*- coding: utf-8 -*-
import json

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from apps.plea.models import CourtEmailCount


class Migration(DataMigration):

    def forwards(self, orm):
        # NOTE: This is a duplicate of the migration 0007_fix_dates, as all of the data generation
        # is done in CourtEmailCount.get_from_context().  However, we still needed a separate migration
        # to reset the CourtEmailCount data.

        # remove all count data
        orm.CourtEmailCount.objects.all().delete()

        # rebuild CourtEmailCount data from CourtEmailPlea.dict_sent
        for obj in orm.CourtEmailPlea.objects.all():
            data = json.loads(obj.dict_sent)
            email_count = CourtEmailCount()

            if email_count.get_from_context(data):
                email_count.save()

                # we need to set the date_sent field again
                # as the column has an auto_add=True
                email_count.date_sent = obj.date_sent
                email_count.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'plea.courtemailcount': {
            'Meta': {'object_name': 'CourtEmailCount'},
            'car_reg_char_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'driver_char_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'hearing_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ni_char_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'sc_chars_count_not_guilty': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'sc_chars_guilty': ('django.db.models.fields.PositiveIntegerField', [], {}),
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
    symmetrical = True
