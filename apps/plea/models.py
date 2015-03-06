from dateutil.parser import parse as date_parse
import datetime as dt

from django.db import models
from django.db.models import Sum, Count


STATUS_CHOICES = (("created_not_sent", "Created but not sent"),
                  ("sent", "Sent"),
                  ("network_error", "Network error"),
                  ("receipt_success", "Processed successfully"),
                  ("receipt_failure", "Processing failed"))


class CourtEmailCountManager(models.Manager):

    def calculate_aggregates(self, start_date, days=7):
        """
        Calculate aggregate stats (subs, guilty pleas, not guilty pleas) over the
        specified date period.
        """
        start_datetime = dt.datetime.combine(
            start_date, dt.datetime.min.time())

        end_datetime = dt.datetime.combine(
            start_date+dt.timedelta(days), dt.datetime.max.time())

        qs = self.filter(
            hearing_date__gte=start_datetime,
            hearing_date__lte=end_datetime)

        totals = qs.aggregate(Sum('total_pleas'),
                              Sum('total_guilty'),
                              Sum('total_not_guilty'))

        return {
            'submissions': qs.count(),
            'pleas': totals['total_pleas__sum'] or 0,
            'guilty': totals['total_guilty__sum'] or 0,
            'not_guilty': totals['total_not_guilty__sum'] or 0
        }

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

        stats['additional']['sc_field_completed'] = {}

        stats['additional']['sc_field_completed']['guilty'] = \
            to_date.filter(sc_guilty_char_count__gte=1).count()

        stats['additional']['sc_field_completed']['not_guilty'] = \
            to_date.filter(sc_not_guilty_char_count__gte=1).count()

        return stats

    def get_stats_by_hearing_date(self, days=None, start_date=None):
        """
        Return stats grouped by hearing date starting from today
        for the number of days specified by days.
        """

        if not start_date:
            start_date = dt.date(2012,01,01)

        results = CourtEmailCount.objects\
            .filter(hearing_date__gte=start_date)\
            .extra({'hearing_day': "date(hearing_date)"})\
            .values('hearing_day')\
            .order_by('hearing_day')\
            .annotate(pleas=Sum('total_pleas'),
                      guilty=Sum('total_guilty'),
                      not_guilty=Sum('total_not_guilty'),
                      submissions=Count('hearing_date'))

        if days:
            results = results[:days]

        return results


class CourtEmailCount(models.Model):
    date_sent = models.DateTimeField(auto_now_add=True)
    total_pleas = models.IntegerField()
    total_guilty = models.IntegerField()
    total_not_guilty = models.IntegerField()
    hearing_date = models.DateTimeField()

    # special circumstances char counts
    sc_guilty_char_count = models.PositiveIntegerField(default=0)
    sc_not_guilty_char_count = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, null=True, blank=True)
    status_info = models.TextField(null=True, blank=True)

    objects = CourtEmailCountManager()

    def get_status_from_case(self, case_obj):
        self.status = case_obj.status
        self.status_info = case_obj.status_info

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

            self.hearing_date = date_part
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

        for plea in context["plea"]["PleaForms"]:
            if plea["guilty"] == "guilty":
                self.sc_guilty_char_count += len(plea.get("guilty_extra", ""))
            else:
                self.sc_not_guilty_char_count += len(plea.get("not_guilty_extra", ""))

        return True


class CaseManager(models.Manager):

    def can_use_urn(self, urn):
        return not self.filter(
            urn__iexact=urn,
            status__in=["sent", "receipt_success"]).exists()


class Case(models.Model):
    """
    The main case model.

    User data is gpg encrypted and persisted to disc then
    transferred to an encrypted S3 account.
    """

    urn = models.CharField(max_length=16, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="created_not_sent")
    status_info = models.TextField(null=True, blank=True)

    objects = CaseManager()


class UsageStatsManager(models.Manager):

    def calculate_weekly_stats(self, to_date=None):
        """
        Occupy UsageStats with the latest weekly aggregate stats.

        This function will create entries in UsageStats for each Monday from
        the last inserted date up to today.

        An associated management command runs this function.
        """

        if not to_date:
            to_date = dt.date.today()

        try:
            last_entry = self.latest('start_date')
        except UsageStats.DoesNotExist:
            # arbitrary Monday start date that is before MAP went live
            start_date = dt.date(2014, 05, 5)
        else:
            start_date = last_entry.start_date + dt.timedelta(7)

        while start_date+dt.timedelta(7) <= to_date:
            totals = CourtEmailCount.objects.calculate_aggregates(start_date, 7)

            UsageStats.objects.create(
                start_date=start_date,
                online_submissions=totals['submissions'],
                online_guilty_pleas=totals['guilty'],
                online_not_guilty_pleas=totals['not_guilty'])

            start_date += dt.timedelta(7)

    def last_six_months(self):
        """
        Get the usage data for the last 6 months
        """

        start_date = dt.date.today() - dt.timedelta(175)

        return self.filter(start_date__gte=start_date)


class UsageStats(models.Model):
    """
    An aggregate table used to store submission data over a 7 day
    period.
    """
    start_date = models.DateField()

    online_submissions = models.PositiveIntegerField(default=0)
    online_guilty_pleas = models.PositiveIntegerField(default=0)
    online_not_guilty_pleas = models.PositiveIntegerField(default=0)

    postal_requisitions = models.PositiveIntegerField(blank=True, null=True)
    postal_responses = models.PositiveIntegerField(blank=True, null=True)

    objects = UsageStatsManager()

    class Meta:
        ordering = ('start_date',)
        verbose_name_plural = "Usage Stats"

