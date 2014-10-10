# -*- coding: utf-8 -*-
import datetime as dt
from dateutil.parser import parse as date_parse
import json

from south.v2 import DataMigration


def populate_from_context(email, context):
    if not "plea" in context:
        return
    if not "PleaForms" in context["plea"]:
        return
    if not "your_details" in context:
        return
    if not "case" in context:
        return

    if email.total_pleas is None:
        email.total_pleas = 0

    if email.total_guilty is None:
        email.total_guilty = 0

    if email.total_not_guilty is None:
        email.total_not_guilty = 0

    try:
        if isinstance(context["case"]["date_of_hearing"], dt.date):
            date_part = context["case"]["date_of_hearing"]
        else:
            date_part = date_parse(context["case"]["date_of_hearing"])

        if isinstance(context["case"]["time_of_hearing"], dt.time):
            time_part = context["case"]["time_of_hearing"]
        else:
            time_part = date_parse(context["case"]["time_of_hearing"]).time()

        email.hearing_date = dt.datetime.combine(date_part, time_part)
    except KeyError:
        return

    for plea_data in context["plea"]["PleaForms"]:
        email.total_pleas += 1

        if plea_data["guilty"] == "guilty":
            email.total_guilty += 1

        if plea_data["guilty"] == "not_guilty":
            email.total_not_guilty += 1

    return email


class Migration(DataMigration):
    def forwards(self, orm):
        # remove all count data
        orm.CourtEmailCount.objects.all().delete()

        # rebuild CourtEmailCount data from CourtEmailPlea.dict_sent
        for obj in orm.CourtEmailPlea.objects.all():
            data = json.loads(obj.dict_sent)
            email_count = orm.CourtEmailCount()
            email_count = populate_from_context(email_count, data)

            if email_count:
                email_count.save()

                # we need to set the date_sent field again
                # as the column has an auto_add=True
                email_count.date_sent = obj.date_sent
                email_count.save()

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")

    models = {
        u'plea.courtemailcount': {
            'Meta': {'object_name': 'CourtEmailCount'},
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hearing_date': ('django.db.models.fields.DateTimeField', [], {}),
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
            'hearing_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_sent'", 'max_length': '30'}),
            'status_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['plea']
    symmetrical = True
