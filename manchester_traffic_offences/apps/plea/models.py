import json

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder


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

    class Meta:
        ordering = ['-date_sent', ]

    def __unicode__(self):
        return "Email to {0} from {1} on {2}".format(self.address_to,
                                                     self.address_from,
                                                     self.date_sent)

    def process_form_data(self, form_data):
        #TODO make this into some sort of JSON thing.
        self.dict_sent = json.dumps(form_data, cls=DjangoJSONEncoder)
