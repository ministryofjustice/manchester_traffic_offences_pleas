from datetime import datetime
import json

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder


class CourtEmailPleaManager(models.Manager):
    @staticmethod
    def delete_old_emails():
        today = datetime.today()
        today_start = datetime(today.year, today.month, today.day)
        old_records = CourtEmailPlea.objects.filter(hearing_date__lt=today_start)
        count = old_records.count()
        old_records.delete()
        return count


class CourtEmailPlea(models.Model):
    STATUS_CHOICES = (("created_not_sent", "Created but not sent"),
                      ("sent", "Sent"),
                      ("network_error", "Network error"))
    date_sent = models.DateTimeField(auto_now_add=True)
    dict_sent = models.TextField(null=True, blank=True)
    subject = models.CharField(max_length=200)
    attachment_text = models.TextField(null=True, blank=True)
    body_text = models.TextField(null=True, blank=True)
    address_from = models.EmailField()
    address_to = models.EmailField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="not_sent")
    status_info = models.TextField(null=True, blank=True)
    hearing_date = models.DateTimeField()

    objects = CourtEmailPleaManager()

    class Meta:
        ordering = ['-date_sent', ]

    def __unicode__(self):
        return "Email to {0} from {1} on {2}".format(self.address_to,
                                                     self.address_from,
                                                     self.date_sent)

    def process_form_data(self, form_data):
        self.dict_sent = json.dumps(form_data, cls=DjangoJSONEncoder)


class CourtEmailCount(models.Model):
    date_sent = models.DateTimeField(auto_now_add=True)
    total_pleas = models.IntegerField()
    total_guilty = models.IntegerField()
    total_not_guilty = models.IntegerField()
    hearing_date = models.DateTimeField()

    def get_from_context(self, context):
        if not "plea" in context:
            return
        if not "PleaForms" in context["plea"]:
            return
        if not "about" in context:
            return
        if not "case" in context:
            return

        if self.total_pleas is None:
            self.total_pleas = 0

        if self.total_guilty is None:
            self.total_guilty = 0

        if self.total_not_guilty is None:
            self.total_not_guilty = 0

        self.hearing_date = context["case"]["date_of_hearing"]

        for plea_data in context["plea"]["PleaForms"]:
            self.total_pleas += 1

            if plea_data["guilty"] == "guilty":
                self.total_guilty += 1

            if plea_data["guilty"] == "not_guilty":
                self.total_not_guilty += 1