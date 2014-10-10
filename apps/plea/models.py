import datetime as dt
import json

from django.db import models
from django.db.models import Sum, Count
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder

from dateutil.parser import parse as date_parse


class CourtEmailPleaManager(models.Manager):
    @staticmethod
    def delete_old_emails():
        today = dt.datetime.today()
        today_start = dt.datetime(today.year, today.month, today.day)
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


class CourtEmailCountManager(models.Manager):

    def get_stats(self):
        """
        Return some basic stats
        """

        def _get_totals(qs):
            totals = qs.aggregate(Sum('total_pleas'), Sum('total_guilty'), Sum('total_not_guilty'))

            return {
                'total': totals['total_pleas__sum'] or 0,
                'guilty': totals['total_guilty__sum'] or 0,
                'not_guilty': totals['total_not_guilty__sum'] or 0
            }

        stats = {
            'submissions': {

            },
            'pleas': {

            }
        }

        now = dt.datetime.now()

        yesterday_filter = {
            "date_sent__gte": dt.datetime.combine(now-dt.timedelta(1), dt.time.min),
            "date_sent__lte": dt.datetime.combine(now-dt.timedelta(1), dt.time.max)
        }

        last_week_filter = {
            "date_sent__gte": dt.datetime.combine(now-dt.timedelta(now.weekday()+7), dt.time.min),
            "date_sent__lte": dt.datetime.combine(now-dt.timedelta(now.weekday()+1), dt.time.max)
        }

        to_date = self.all()
        last_week = self.filter(**last_week_filter)
        yesterday = self.filter(**yesterday_filter)

        stats['submissions']['to_date'] = to_date.count()
        stats['submissions']['last_week'] = last_week.count()
        stats['submissions']['yesterday'] = yesterday.count()

        stats['pleas']['to_date'] = _get_totals(to_date)
        stats['pleas']['last_week'] = _get_totals(last_week)
        stats['pleas']['yesterday'] = _get_totals(yesterday)

        stats['additional'] = {}

        total_optional = to_date.filter(Q(national_insurance_char_count__gte=8) |
                                        Q(driving_licence_char_count__gte=8) |
                                        Q(registration_char_count__gte=8)).count()

        pc_optional = total_optional / (stats['submissions']['to_date'] / 100.0)

        stats['additional']['subs_with_optional_fields_percentage'] = pc_optional

        stats['additional']['sc_field_completed'] = {}

        stats['additional']['sc_field_completed']['guilty'] = \
            to_date.filter(sc_guilty_char_count__gte=1).count()

        stats['additional']['sc_field_completed']['not_guilty'] = \
            to_date.filter(sc_not_guilty_char_count__gte=1).count()

        return stats

    def get_stats_by_hearing_date(self, days=3):
        """
        Return stats grouped by hearing date starting from today
        for the number of days specified by days.
        """
        now = dt.datetime.now()

        start_date = now - dt.timedelta(now.weekday())

        results = CourtEmailCount.objects\
            .filter(hearing_date__gte=start_date)\
            .extra({'hearing_day': "date(hearing_date)"})\
            .values('hearing_day')\
            .order_by('hearing_day')\
            .annotate(pleas=Sum('total_pleas'),
                      guilty=Sum('total_guilty'),
                      not_guilty=Sum('total_not_guilty'),
                      submissions=Count('hearing_date'))[:days]

        return results


class CourtEmailCount(models.Model):
    date_sent = models.DateTimeField(auto_now_add=True)
    total_pleas = models.IntegerField()
    total_guilty = models.IntegerField()
    total_not_guilty = models.IntegerField()
    hearing_date = models.DateTimeField()

    # special circumbstances char counts
    sc_guilty_char_count = models.PositiveIntegerField(default=0)
    sc_not_guilty_char_count = models.PositiveIntegerField(default=0)

    national_insurance_char_count = models.PositiveIntegerField(default=0)
    driving_licence_char_count = models.PositiveIntegerField(default=0)
    registration_char_count = models.PositiveIntegerField(default=0)

    objects = CourtEmailCountManager()

    def get_from_context(self, context):
        if not "plea" in context:
            return
        if not "PleaForms" in context["plea"]:
            return
        if not "your_details" in context:
            return
        if not "case" in context:
            return

        if self.total_pleas is None:
            self.total_pleas = 0

        if self.total_guilty is None:
            self.total_guilty = 0

        if self.total_not_guilty is None:
            self.total_not_guilty = 0

        try:
            if isinstance(context["case"]["date_of_hearing"], dt.date):
                date_part = context["case"]["date_of_hearing"]
            else:
                date_part = date_parse(context["case"]["date_of_hearing"])

            if isinstance(context["case"]["time_of_hearing"], dt.time):
                time_part = context["case"]["time_of_hearing"]
            else:
                time_part = date_parse(context["case"]["time_of_hearing"]).time()

            self.hearing_date = dt.datetime.combine(date_part, time_part)
        except KeyError:
            return False

        for plea_data in context["plea"]["PleaForms"]:
            self.total_pleas += 1

            if plea_data["guilty"] == "guilty":
                self.total_guilty += 1

            if plea_data["guilty"] == "not_guilty":
                self.total_not_guilty += 1

        # extra anon information
        self.sc_guilty_char_count, self.sc_not_guilty_char_count = 0, 0

        for plea in context['plea']['PleaForms']:
            if plea['guilty'] == "guilty":
                self.sc_guilty_char_count += len(plea['mitigations'])
            else:
                self.sc_not_guilty_char_count += len(plea['mitigations'])

        self.national_insurance_char_count = len(context['your_details']['national_insurance_number'])
        self.driving_licence_char_count = len(context['your_details']['driving_licence_number'])
        self.registration_char_count = len(context['your_details']['registration_number'])

        return True
