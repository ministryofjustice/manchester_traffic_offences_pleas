# -*- coding: utf-8 -*-
import json
import datetime as dt

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from dateutil.parser import parse as date_parse

from apps.plea.models import CourtEmailCount


def get_from_context(email_count_obj, context):
    """
    A slightly modified copy of CourtEmailCount.get_from_context()
    """
    
    if not "plea" in context:
        return
    if not "PleaForms" in context["plea"]:
        return
    if not "your_details" in context:
        return
    if not "case" in context:
        return

    if email_count_obj.total_pleas is None:
        email_count_obj.total_pleas = 0

    if email_count_obj.total_guilty is None:
        email_count_obj.total_guilty = 0

    if email_count_obj.total_not_guilty is None:
        email_count_obj.total_not_guilty = 0

    try:
        if isinstance(context["case"]["date_of_hearing"], dt.date):
            date_part = context["case"]["date_of_hearing"]
        else:
            date_part = date_parse(context["case"]["date_of_hearing"])

        if isinstance(context["case"]["time_of_hearing"], dt.time):
            time_part = context["case"]["time_of_hearing"]
        else:
            time_part = date_parse(context["case"]["time_of_hearing"]).time()

        email_count_obj.hearing_date = dt.datetime.combine(date_part, time_part)
    except KeyError:
        return False

    for plea_data in context["plea"]["PleaForms"]:
        email_count_obj.total_pleas += 1

        if plea_data["guilty"] == "guilty":
            email_count_obj.total_guilty += 1

        if plea_data["guilty"] == "not_guilty":
            email_count_obj.total_not_guilty += 1

    # extra anon information
    email_count_obj.sc_guilty_char_count, email_count_obj.sc_not_guilty_char_count = 0, 0

    for plea in context['plea']['PleaForms']:
        if plea['guilty'] == "guilty":
            email_count_obj.sc_guilty_char_count += len(plea['mitigations'])
        else:
            email_count_obj.sc_not_guilty_char_count += len(plea['mitigations'])

    email_count_obj.national_insurance_char_count = len(context['your_details']['national_insurance_number'])
    email_count_obj.driving_licence_char_count = len(context['your_details']['driving_licence_number'])
    email_count_obj.registration_char_count = len(context['your_details']['registration_number'])


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

            if get_from_context(email_count, data):
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
