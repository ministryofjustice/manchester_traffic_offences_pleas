from collections import Counter
from dateutil.parser import parse as date_parse
import datetime as dt

from django.db import models
from django.db.models import Sum, Count, F
from django.utils.translation import get_language
from django.contrib.postgres.fields import HStoreField

from standardisers import standardise_name, StandardiserNoOutputException, standardise_urn


STATUS_CHOICES = (("created_not_sent", "Created but not sent"),
                  ("sent", "Sent"),
                  ("network_error", "Network error"),
                  ("receipt_success", "Processed successfully"),
                  ("receipt_failure", "Processing failed"))


COURT_LANGUAGE_CHOICES = (("en", "English"),
                          ("cy", "Welsh"))


INITIATION_TYPE_CHOICES = (("C", "Charge"),
                           ("J", "SJP"),
                           ("Q", "Requisition"),
                           ("O", "Other"),
                           ("R", "Remitted"),
                           ("S", "Summons"))

NOTICE_TYPES_CHOICES = (("both", "Both"),
                        ("sjp", "SJP"),
                        ("non-sjp", "Non-SJP"))


def get_totals(qs):
    totals = qs.aggregate(Sum('total_pleas'),
                          Sum('total_guilty'),
                          Sum('total_not_guilty'))

    return {
        'submissions': qs.count(),
        'pleas': totals['total_pleas__sum'] or 0,
        'guilty': totals['total_guilty__sum'] or 0,
        'not_guilty': totals['total_not_guilty__sum'] or 0
    }


class CourtEmailCountManager(models.Manager):
    def calculate_aggregates(self, start_date, days=7):
        """
        Calculate aggregate stats (submissions, total pleas,
        guilty pleas, not guilty pleas) over the specified date period.
        """
        start_datetime = start_date

        end_datetime = start_date + dt.timedelta(days)

        qs = self.filter(sent=True,
                         court__test_mode=False,
                         date_sent__gte=start_datetime,
                         date_sent__lt=end_datetime)

        totals = get_totals(qs)

        return totals

    def get_stats(self, start=None, end=None):
        """
        Return stats, which can be filtered by start date or end date
        """
        qs = self.filter(sent=True, court__test_mode=False)

        if start:
            qs = qs.filter(date_sent__gte=start)

        if end:
            qs = qs.filter(date_sent__lte=end)

        return get_totals(qs)

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

    def get_stats_by_court(self, start=None, end=None):
        """
        Return stats grouped by court
        """
        courts = Court.objects.filter(test_mode=False)

        stats = []

        for court in courts:

            qs = self.filter(sent=True,
                             court__id=court.id)

            if start:
                qs = qs.filter(date_sent__gte=start)

            if end:
                qs = qs.filter(date_sent__lte=end)

            data = {"court_name": court.court_name,
                    "region_code": court.region_code}

            data.update(get_totals(qs))

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
    court = models.ForeignKey("Court", related_name="court_email_counts")
    initiation_type = models.CharField(max_length=2, null=False, blank=False, default="Q",
                                       choices=INITIATION_TYPE_CHOICES)
    language = models.CharField(max_length=2, null=False, blank=False, default="en",
                                choices=COURT_LANGUAGE_CHOICES)

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
        if "data" not in context["plea"]:
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
            if isinstance(context["case"]["contact_deadline"], dt.date):
                date_part = context["case"]["contact_deadline"]
            else:
                date_part = date_parse(context["case"]["contact_deadline"])

            self.hearing_date = date_part
        except KeyError:
            return False

        self.initiation_type = "J" if context["notice_type"]["sjp"] else "Q"
        self.language = get_language().split("-")[0]

        for plea_data in context["plea"]["data"]:
            self.total_pleas += 1

            if plea_data["guilty"] == "guilty":
                self.total_guilty += 1

            if plea_data["guilty"] == "not_guilty":
                self.total_not_guilty += 1

        # extra anon information
        self.sc_guilty_char_count, self.sc_not_guilty_char_count = 0, 0

        for plea in context["plea"]["data"]:
            if plea["guilty"] == "guilty":
                self.sc_guilty_char_count += len(plea.get("guilty_extra", ""))
            else:
                self.sc_not_guilty_char_count += len(plea.get("not_guilty_extra", ""))

        return True


class CaseManager(models.Manager):
    class Meta:
        ordering = ["offence_seq_number"]

    def can_use_urn(self, urn, first_name, last_name):
        name = standardise_name(first_name, last_name)

        cases = self.filter(urn__iexact=urn, sent=True)

        for case in cases:
            if case.extra_data and case.extra_data.get("OrganisationName"):
                return False
            elif case.name == name:
                return False
        return True


class Case(models.Model):
    """
    The main case model.

    User data is gpg encrypted and persisted to disc then
    transferred to an encrypted S3 account.
    """
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    urn = models.CharField(max_length=30, db_index=True)

    extra_data = HStoreField(null=True, blank=True)

    case_number = models.CharField(max_length=12, null=True, blank=True,
                                   help_text="as supplied by DX")

    name = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    email_permission = models.BooleanField(default=False)

    date_of_hearing = models.DateField(null=True, blank=True)
    imported = models.BooleanField(default=False)

    ou_code = models.CharField(max_length=10, null=True, blank=True)
    initiation_type = models.CharField(max_length=2, null=False, blank=False, default="Q",
                                       choices=INITIATION_TYPE_CHOICES)
    language = models.CharField(max_length=2, null=False, blank=False, default="en",
                                choices=COURT_LANGUAGE_CHOICES)

    sent = models.BooleanField(null=False, default=False)
    processed = models.BooleanField(null=False, default=False)

    objects = CaseManager()

    completed_on = models.DateTimeField(
        blank=True, null=True,
        help_text="The date/time a user completes a submission.")

    def add_action(self, status, status_info):
        self.actions.create(status=status, status_info=status_info)

    def has_action(self, status):
        return self.actions.filter(status=status).exists()

    def get_actions(self, status):
        return self.actions.filter(status=status)

    def get_users_name(self):
        """
        Attempt to get the user's name
        """

        if self.name:
            return self.name

        if self.extra_data and "Forename1" in self.extra_data:
            return "{} {}".format(self.extra_data["Forename1"], self.extra_data["Surname"])

        return ""

    def can_auth(self):
        """
        Do we have the relevant data to authenticate the user?
        """

        return self.extra_data and "PostCode" in self.extra_data and self.extra_data["PostCode"]


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
    offence_short_title_welsh = models.CharField(max_length=120, null=True, blank=True)
    offence_wording = models.TextField(max_length=4000)
    offence_wording_welsh = models.TextField(max_length=4000, null=True, blank=True)
    offence_seq_number = models.CharField(max_length=10, null=True, blank=True)


class CaseOffenceFilter(models.Model):
    filter_match = models.CharField(max_length=20)
    description = models.CharField(max_length=500, null=True, blank=True)


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

    def get_by_standardised_urn(self, urn):
        """
        Standardise the URN before matching it
        """
        try:
            return Court.objects.get_by_urn(standardise_urn(urn))
        except StandardiserNoOutputException:
            return False


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
        verbose_name="URN Region Code",
        help_text="The initial two digit URN number, e.g. 06",
        unique=True)

    court_name = models.CharField(
        max_length=255)

    court_address = models.TextField()

    court_telephone = models.CharField(
        max_length=50)

    court_email = models.CharField(
        max_length=255,
        help_text="The email address for users to contact the court")

    court_language = models.CharField(max_length=4, null=False, blank=False, default="en",
                                      choices=COURT_LANGUAGE_CHOICES)

    submission_email = models.CharField(
        verbose_name="Internal contact details",
        max_length=255,
        help_text="The outbound court email used to send submission data")

    court_receipt_email = models.CharField(
        verbose_name="Plea receipt email",
        max_length=255, null=True, blank=True,
        help_text="The email address to send receipts confirming the plea has been filed correctly")

    local_receipt_email = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The inbound receipt email address. Used for validation purposes.")

    plp_email = models.CharField(
        verbose_name="Police submission email",
        max_length=255,
        help_text="The email address provided by the police to receive pleas",
        null=True,
        blank=True)

    enabled = models.BooleanField(
        verbose_name="Live",
        default=False)

    test_mode = models.BooleanField(
        default=False,
        help_text="Is this court entry used for testing purposes?")

    notice_types = models.CharField(
        max_length=7, null=False, blank=False, default="both",
        choices=NOTICE_TYPES_CHOICES,
        help_text="What kind of notices are being sent out by this area?")

    validate_urn = models.BooleanField(
        default=False,
        help_text="Do we have a full set of incoming DX data?"
    )

    display_case_data = models.BooleanField(
        default=False,
        help_text="Display the updated plea page for cases that have offence data attached"
    )

    ou_code = models.CharField(max_length=10, null=True, blank=True)

    enforcement_email = models.CharField(
        verbose_name="Email address of the enforcement team",
        max_length=255, null=True, blank=True,
        help_text="")

    enforcement_telephone = models.CharField(
        verbose_name="Email address of the enforcement team",
        max_length=255, null=True, blank=True,
        help_text="")

    def __unicode__(self):
        return "{} / {} / {}".format(self.court_code,
                                     self.region_code,
                                     self.court_name)

    objects = CourtManager()


class DataValidation(models.Model):
    date_entered = models.DateTimeField(auto_now_add=True)
    urn_entered = models.CharField(max_length=50, null=False, blank=False)
    urn_standardised = models.CharField(max_length=50, null=False, blank=False)
    urn_formatted = models.CharField(max_length=50, null=False, blank=False)
    case_match = models.ForeignKey("plea.Case", null=True, blank=True)
    case_match_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date_entered"]

