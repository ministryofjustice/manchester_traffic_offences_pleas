from collections import Counter
from dateutil.parser import parse as date_parse
import datetime as dt

from django.db import models
from django.db.models import Sum, Count, F


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
            'submissions': {},
            'pleas': {}
        }

        to_date = self.filter(sent=True, court__test_mode=False)

        stats['submissions']['to_date'] = to_date.count()

        stats['pleas']['to_date'] = _get_totals(to_date)

        return stats

    def get_stats_by_hearing_date(self, days=None, start_date=None):
        """
        Return stats grouped by hearing date starting from today
        for the number of days specified by days.
        """

        if not start_date:
            start_date = dt.date(2012,01,01)

        results = CourtEmailCount.objects\
            .filter(sent=True,
                    hearing_date__gte=start_date,
                    court__test_mode=False)\
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

    def get_stats_by_court(self):
        """
        Return stats grouped by court
        """
        courts = Court.objects.filter(test_mode=False)

        stats = []

        for court in courts:

            qs = self.filter(sent=True,
                             court__id=court.id)

            totals = qs.aggregate(Sum('total_pleas'), Sum('total_guilty'), Sum('total_not_guilty'))

            data = {"court_name": court.court_name,
                    "region_code": court.region_code,
                    "submissions": qs.count(),
                    "pleas": totals['total_pleas__sum'],
                    "guilty": totals['total_guilty__sum'],
                    "not_guilty": totals['total_not_guilty__sum']}

            stats.append(data)

        return stats

    def get_stats_days_from_hearing(self, limit=60):
        courts = Court.objects.filter(test_mode=False)

        counts = CourtEmailCount.objects.filter(court__in=courts).annotate(num_days=F('hearing_date') - F('date_sent')).values('num_days').order_by("-num_days")
        day_counts = Counter([x["num_days"].days for x in counts if x["num_days"].days < limit and x["num_days"].days > 0])

        for day_number in range(limit):
            if day_number not in day_counts.keys():
                day_counts[day_number] = 0

        return day_counts

class CourtEmailCount(models.Model):
    date_sent = models.DateTimeField(auto_now_add=True)
    court = models.ForeignKey("Court")

    total_pleas = models.IntegerField()
    total_guilty = models.IntegerField()
    total_not_guilty = models.IntegerField()
    hearing_date = models.DateTimeField()

    # special circumstances char counts
    sc_guilty_char_count = models.PositiveIntegerField(default=0)
    sc_not_guilty_char_count = models.PositiveIntegerField(default=0)

    sent = models.BooleanField(null=False, default=False)
    processed = models.BooleanField(null=False, default=False)

    objects = CourtEmailCountManager()

    def get_status_from_case(self, case_obj):
        self.sent = case_obj.sent
        self.processed = case_obj.processed

    def get_from_context(self, context, court):
        if "plea" not in context:
            return
        if "PleaForms" not in context["plea"]:
            return
        if "your_details" not in context:
            return
        if "case" not in context:
            return

        if self.total_pleas is None:
            self.total_pleas = 0

        if self.total_guilty is None:
            self.total_guilty = 0

        if self.total_not_guilty is None:
            self.total_not_guilty = 0

        self.court = court

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
    class Meta:
        ordering = ["offence_seq_number"]

    def can_use_urn(self, urn):
        return not self.filter(
            urn__iexact=urn,
            sent=True).exists()


class Case(models.Model):
    """
    The main case model.

    User data is gpg encrypted and persisted to disc then
    transferred to an encrypted S3 account.
    """

    urn = models.CharField(max_length=16, db_index=True)

    title = models.CharField(max_length=35, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    forenames = models.CharField(max_length=105, null=True, blank=True,
                                 help_text="as supplied by DX")
    surname = models.CharField(max_length=35, null=True, blank=True,
                               help_text="as supplied by DX")

    case_number = models.CharField(max_length=12, null=True, blank=True,
                                   help_text="as supplied by DX")

    ou_code = models.CharField(max_length=10, null=True, blank=True)

    sent = models.BooleanField(null=False, default=False)
    processed = models.BooleanField(null=False, default=False)

    objects = CaseManager()

    def add_action(self, status, status_info):
        self.actions.create(status=status, status_info=status_info)

    def has_action(self, status):
        return self.actions.filter(status=status).exists()

    def get_actions(self, status):
        return self.actions.filter(status=status)


class CaseAction(models.Model):
    case = models.ForeignKey(Case, related_name="actions", null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, null=False, blank=False)
    status_info = models.TextField(null=True, blank=True)

    class Meta:
        get_latest_by = 'date'


class Offence(models.Model):
    case = models.ForeignKey(Case, related_name="offences")

    offence_code = models.CharField(max_length=10, null=True, blank=True)
    offence_short_title = models.CharField(max_length=120)
    offence_wording = models.TextField(max_length=4000)
    offence_seq_number = models.CharField(max_length=10, null=True, blank=True)


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


class CourtManager(models.Manager):
    def has_court(self, urn):
        """
        Take a URN and return True if the region_code is valid
        """

        try:
            self.get(region_code=urn[:2],
                     enabled=True)

            return True

        except Court.DoesNotExist:
            return False

    def get_by_urn(self, urn):
        """
        Retrieve court model by URN
        """

        return self.get(region_code=urn[:2],
                        enabled=True)

    def validate_emails(self, sending_email, receipt_email):
        try:
            self.get(court_receipt_email__iexact=sending_email,
                     local_receipt_email__iexact=receipt_email,
                     enabled=True)

            return True

        except Court.DoesNotExist:
            return False


class Court(models.Model):
    court_code = models.CharField(
        max_length=100, null=True, blank=True)

    region_code = models.CharField(
        max_length=2,
        help_text="The initial two digit URN number, e.g. 06",
        unique=True)

    court_name = models.CharField(
        max_length=255)

    court_address = models.TextField()

    court_telephone = models.CharField(
        max_length=50)

    court_email = models.CharField(
        max_length=255,
        help_text="A user facing email address")

    submission_email = models.CharField(
        max_length=255,
        help_text="The outbound court email used to send submission data")

    court_receipt_email = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The email address the court uses to send receipt emails to MaP")

    local_receipt_email = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The inbound receipt email address. Used for validation purposes.")

    plp_email = models.CharField(
        max_length=255,
        help_text="The PLP outbound email - if left empty the PLP email won't be sent",
        null=True,
        blank=True)

    enabled = models.BooleanField(
        default=False)

    test_mode = models.BooleanField(
        default=False,
        help_text="Is this court entry used for testing purposes?")

    validate_urn = models.BooleanField(
        default=False,
        help_text="Do we have a full set of incoming DX data?"
    )

    display_case_data = models.BooleanField(
        default=False,
        help_text="Display the updated plea page for cases that have offence data attached"
    )

    def __unicode__(self):
        return "{} / {} / {}".format(self.court_code,
                                     self.region_code,
                                     self.court_name)

    objects = CourtManager()






