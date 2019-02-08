from collections import Counter
from dateutil.parser import parse as date_parse
import datetime as dt

from django.db import models
from django.db.models import Sum, Count, F
from django.utils.translation import get_language
from django.contrib.postgres.fields import HStoreField
from django.core.exceptions import ValidationError

from .exceptions import *
from .standardisers import (
    standardise_name, StandardiserNoOutputException, standardise_urn,
    standardise_postcode
)

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
                          Sum('total_not_guilty'),
                          Sum('total_guilty_court'),
                          Sum('total_guilty_no_court'))
    return {
        'submissions': qs.count(),
        'pleas': totals['total_pleas__sum'] or 0,
        'guilty': totals['total_guilty__sum'] or 0,
        'not_guilty': totals['total_not_guilty__sum'] or 0,
        'guilty_court': totals['total_guilty_court__sum'] or 0,
        'guilty_no_court': totals['total_guilty_no_court__sum'] or 0
    }


class CourtEmailCountManager(models.Manager):
    def calculate_aggregates(self, start_date,court, days=7):
        """
        Calculate aggregate stats (submissions, total pleas,
        guilty pleas, not guilty pleas) over the specified date period.
        """
        start_datetime = start_date

        end_datetime = start_date + dt.timedelta(days)

        qs = self.filter(sent=True,
                         court__test_mode=False,
                         date_sent__gte=start_datetime,
                         date_sent__lt=end_datetime,
                         court=court)

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
            start_date = dt.date(2012, 1, 1)

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
    total_guilty_court = models.IntegerField(null=True, blank=True, default=0)
    total_guilty_no_court = models.IntegerField(null=True, blank=True,default=0)
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

        if self.total_guilty_court is None:
            self.total_guilty_court = 0

        if self.total_guilty_no_court is None:
            self.total_guilty_no_court = 0

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

            if plea_data["guilty"] == "guilty" or plea_data["guilty"] == "guilty_court" or plea_data["guilty"] == "guilty_no_court":
                self.total_guilty += 1

            if plea_data["guilty"] == "guilty_court":
                self.total_guilty_court += 1

            if plea_data["guilty"] == "guilty_no_court":
                self.total_guilty_no_court += 1

            if plea_data["guilty"] == "not_guilty":
                self.total_not_guilty += 1

        # extra anon information
        self.sc_guilty_char_count, self.sc_not_guilty_char_count = 0, 0

        for plea in context["plea"]["data"]:
            if plea["guilty"] == "guilty_court" or plea["guilty"] == "guilty_no_court":
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

    def get_case_for_urn(self, urn):
        """
        Can the user use this URN for a DX based submission?
        """

        cases = self.filter(urn__iexact=urn, sent=False, imported=True)

        if not cases or cases.count() > 1 or not cases[0].can_auth():
            return None

        return cases[0]


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
    initiation_type = models.CharField(max_length=2,
                                       null=False,
                                       blank=False,
                                       default="Q",
                                       choices=INITIATION_TYPE_CHOICES)

    language = models.CharField(max_length=2, null=False, blank=False,
                                default="en", choices=COURT_LANGUAGE_CHOICES)

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
            return "{} {}".format(self.extra_data["Forename1"],
                                  self.extra_data["Surname"])

        return ""

    def can_auth(self):
        """
        Do we have the relevant data to authenticate the user?
        """

        return self.extra_data and ("PostCode" in self.extra_data or "DOB" in self.extra_data)

    def has_valid_doh(self):
        today = dt.date.today()
        if self.date_of_hearing:
            return self.date_of_hearing >= today
        else:
            return False

    def authenticate(self, num_charges, postcode, dob):

        postcode_match, dob_match = False, False

        assert postcode or dob, "Provide at least one value"

        if not self.can_auth():
            return False

        if postcode and "PostCode" in self.extra_data:
            inputted_postcode = standardise_postcode(postcode)
            stored_postcode = standardise_postcode(
                self.extra_data.get("PostCode"))

            postcode_match = inputted_postcode == stored_postcode

        if dob and "DOB" in self.extra_data:
            dob_match = dob == date_parse(self.extra_data["DOB"]).date()
        return self.offences.count() == num_charges and (postcode_match or dob_match)

    def auth_field(self):
        """
        Determine which field to use for auth
        """

        if self.extra_data:
            if "DOB" in self.extra_data:
                return "DOB"
            elif "PostCode" in self.extra_data:
                return "PostCode"

        return None

    def __str__(self):
        return "{} / {}".format(
            self.urn,
            self.case_number,
        )

    def _get_initiation_type_choice(self):
        for initiation_type in INITIATION_TYPE_CHOICES:
            try:
                if initiation_type[0] == self.initiation_type:
                    return initiation_type
            except AttributeError:
                pass

    def save(self, *args, **kwargs):
        super(Case, self).save(*args, **kwargs)
        AuditEvent().populate(
            case=self,
            event_type="case_model",
            event_subtype="success",
            event_trace="Case {0} was updated".format(self.urn),
            **kwargs)


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
            start_date = dt.date(2014, 5, 5)
        else:
            start_date = last_entry.start_date + dt.timedelta(7)

        court_list = Court.objects.filter(test_mode=False)

        while start_date + dt.timedelta(7) <= to_date:
            for c in court_list:
                totals = CourtEmailCount.objects.calculate_aggregates(start_date,c,7)
                UsageStats.objects.create(
                    start_date=start_date,
                    court=c,
                    online_submissions=totals['submissions'],
                    online_guilty_pleas=totals['guilty'],
                    online_not_guilty_pleas=totals['not_guilty'],
                    online_guilty_attend_court_pleas=totals['guilty_court'],
                    online_guilty_no_court_pleas=totals['guilty_no_court'])

            start_date += dt.timedelta(7)


        # while start_date+dt.timedelta(7) <= to_date:
        #     totals = CourtEmailCount.objects.calculate_aggregates(start_date, 7)
        #
        #     UsageStats.objects.create(
        #         start_date=start_date,
        #         online_submissions=totals['submissions'],
        #         online_guilty_pleas=totals['guilty'],
        #         online_not_guilty_pleas=totals['not_guilty'],
        #         online_guilty_attend_court_pleas=totals['guilty_court'],
        #         online_guilty_no_court_pleas=totals['guilty_no_court'])
        #
        #     start_date += dt.timedelta(7)

    def last_six_months(self):
        """
        Get the usage data for the last 6 months and usage data per week
        """

        start_date = dt.date.today() - dt.timedelta(175)


        stats_per_week = self.filter(start_date__gte=start_date).values('start_date').annotate(online_submissions=Sum('online_submissions'),
                                                                                               online_guilty_pleas=Sum('online_guilty_pleas'),
                                                                                               online_not_guilty_pleas=Sum('online_not_guilty_pleas'),
                                                                                               online_guilty_attend_court_pleas=Sum('online_guilty_attend_court_pleas'),
                                                                                               online_guilty_no_court_pleas=Sum('online_guilty_no_court_pleas'),
                                                                                               postal_requisitions=Sum('postal_requisitions'),
                                                                                               postal_responses=Sum('postal_responses'))

        return stats_per_week

class UsageStats(models.Model):
    """
    An aggregate table used to store submission data over a 7 day
    period.
    """
    start_date = models.DateField()
    court = models.ForeignKey('Court', blank=True, null=True)

    online_submissions = models.PositiveIntegerField(default=0)
    online_guilty_pleas = models.PositiveIntegerField(default=0)
    online_not_guilty_pleas = models.PositiveIntegerField(default=0)
    online_guilty_attend_court_pleas = models.PositiveIntegerField(blank=True, null=True, default=0)
    online_guilty_no_court_pleas = models.PositiveIntegerField(blank=True, null=True, default=0)
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
        return self.filter(region_code=urn[:2],
                           enabled=True).exists()

    def get_by_urn(self, urn):
        """
        Retrieve court model by URN
        """

        courts = self.filter(region_code=urn[:2],
                             enabled=True).order_by("id")

        if courts:
            return courts[0]
        else:
            raise Court.DoesNotExist

    def get_court(self, urn, ou_code=None):
        """
        Attempt to return the court by URN or ou code.

        Prioritise matching on ou code but if there is no match then
        attempt to match on URN
        """

        if ou_code:
            try:
                return Court.objects.get(
                    oucode__ou_code=ou_code[:5],
                    region_code=urn[:2])
            except Court.DoesNotExist:
                pass

        return self.get_by_urn(urn)

    def get_court_by_ou_code(self, ou_code):
        return self.select_related().get(oucode__ou_code=ou_code[:4])

    def get_court_dx(self, urn):
        """
        Get court whilst using DX data and ou-code matching where possible
        """

        try:
            ou_code = Case.objects.get(urn=standardise_urn(urn),
                                       imported=True,
                                       ou_code__isnull=False).ou_code

        except (Case.DoesNotExist,
                Case.MultipleObjectsReturned,
                StandardiserNoOutputException):
            ou_code = None

        return self.get_court(urn, ou_code=ou_code)

    def get_by_standardised_urn(self, urn):
        """
        Standardise the URN before matching it
        """
        try:
            return self.get_by_urn(standardise_urn(urn))
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
        help_text="The initial two digit URN number, e.g. 06")

    court_name = models.CharField(
        max_length=255)

    court_address = models.TextField()

    court_telephone = models.CharField(
        max_length=50)

    court_email = models.CharField(
        max_length=255,
        help_text="The email address for users to contact the court")

    court_language = models.CharField(max_length=4,
                                      null=False,
                                      blank=False,
                                      default="en",
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

    enforcement_email = models.CharField(
        verbose_name="Email address of the enforcement team",
        max_length=255, null=True, blank=True,
        help_text="")

    enforcement_telephone = models.CharField(
        verbose_name="Telephone number of the enforcement team",
        max_length=255, null=True, blank=True,
        help_text="")

    def __str__(self):
        return "{} / {} / {}".format(self.court_code,
                                     self.region_code,
                                     self.court_name)

    objects = CourtManager()

    def supports_language(self, lang_code):
        if self.court_language.lower() == "cy":
            return True
        elif self.court_language == lang_code[:2]:
            return True
        else:
            return False

    def clean(self):
        if not self.submission_email.endswith(('@hmcts.gsi.gov.uk', '@justice.gov.uk', '@hmcts.net')):
            raise ValidationError('Not allowed court email domain')


class OUCode(models.Model):
    court = models.ForeignKey(Court)
    ou_code = models.CharField(max_length=5, unique=True,
                               help_text="The first five digits of an OU code")


class DataValidation(models.Model):
    date_entered = models.DateTimeField(auto_now_add=True)
    urn_entered = models.CharField(max_length=50, null=False, blank=False)
    urn_standardised = models.CharField(max_length=50, null=False, blank=False)
    urn_formatted = models.CharField(max_length=50, null=False, blank=False)
    case_match = models.ForeignKey("plea.Case", null=True, blank=True)
    case_match_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date_entered"]


class AuditEvent(models.Model):
    """
    Keep track of events involving URNs to ensure data integrity throughout the
    pipeline and give staff a better view of potential issues.

    Usage:

        a = AuditEvent()
        a.create(data)

    where data is a dictionary that must contain an event_type and event_subtype
    and may contain a case, result, form or arbitrary fields.

    Considerations:

     * Cases
     * Form validation errors
     * API validation, creation and updates
     * Pre-processing steps

    1. User actions (all occur during the user journey)

     * User entered URN but not in system
     * User entered URN but already submitted
     * User entered URN but failed validation

    2. Soap gateway/DX import actions (all occur at the REST endpoint which is managed by the main application)

     * Urn imported successfully
     * Urn invalid (often this is because of a lack of URN so there may not be a specific action to report)
     * Case already in system - not importing
     * Case offences fail white list

    3. Resulting actions (all occur in the application but run via a cron'd django management command)

     * Result received but already sent
     * Partial result received - not resulting
     * Result email sent to {email address}
     * Result contains out of scope offence - not resulting

    4. Search

    I'd envisage an admin screen that allows Katie et al. to
    enter a URL
    and see an audit trail.  Here's my attempt a mockup:

    ------------------------------------------------------------------------------

    Search URN:  [ 41xx00011100 ]

    {timestamp} :   App: User entered URN but not in system
    {timestamp} :   DX: Case imported
    {timestamp} :   DX: Duplicate case - not importing
    {timestamp} :   App: User failed validation
    {timestamp} :   App: User completed submission.
    {timestamp} :   Resulting: Partial result received - not
    resulting
    {timestamp} :   Resulting: result email sent

    5. Hash of hstore


    Tests
    =====

    There are several parts and code paths to test, not all will be tested in the same place

    API:
        Load a Case via the API
            Success - all required fields present - the Case was saved, the AuditEvent was saved
            Failure - required data was missing - the Case was not saved, the AuditEvent was saved
            Failure - invalid field types - the Case was not saved, the AuditEvent was saved
        Load an AuditEvent via the API
            Success - the AuditEvent was saved with details of the pre-import failure
            Failure - bad event type

    Frontend (cucumber tests):
        User journey success - The user is able to plea
        User journey failure - The user is not able to plea because URN is not in the database
        User journey failure - The user is not able to plea because the name is wrong
        User journey failure - The user is not able to plea because the postcode is wrong

    Admin Interface (cucumber tests):
        Login / logout - user able to log in and out
        Roles / Permissions - Service managers should have access to audit events but court staff should not
        The service manager should be able to see audit events
        Audiit events should be sortable
        Audit events should be filterable
        Audit events should be linked to the case where possible
    """

    EVENT_TYPE_CHOICES = (
        ("not_set", "Not Set"),  # programming error - caller did not set event_type
        ("case_model", "Case Save event"),  # save operations on the model
        ("case_form", "Case Form event"),  # form validation issues
        ("case_api", "Case API event"),  # issue at the Case api
        ("urn_validator", "URN validation event"),  # issue vaidating a URN
        ("result_api", "Result API event"),  # issue at the Result api
        ("auditevent_api", "AuditEvent API event"),  # issue with an external component
    )
    EVENT_SUBTYPE_CHOICES = (
        ("not_set", "Not set"),
        ("success", "Success"),
        ("EXT1", "External failure 1"),
        ("EXT2", "External failure 2"),
        ("case_strict_validation_failed", "Form Validation Error: Strict"),
        ("case_loose_validation_failed", "Form Validation Error: Loose"),
        ("case_invalid_missing_name", "Invalid Case: Missing Name"),
        ("case_invalid_missing_urn", "Invalid Case: Missing URN"),
        ("case_invalid_invalid_urn", "Invalid Case: Invalid URN"),
        ("case_invalid_missing_dateofhearing", "Invalid Case: Missing date of hearing"),
        ("case_invalid_name_too_long", "Invalid Case: Name too long"),
        ("case_invalid_offencecode", "Invalid Case: Invalid offence code"),
        ("case_invalid_courtcode", "Invalid Case: Invalid court code"),
        ("case_invalid_not_in_whitelist", "Invalid Case: Not in whitelist"),
        ("case_invalid_invalid_initiation_type", "Invalid Case: Initiation type not accepted"),
        ("case_invalid_duplicate_offence", "Invalid Case: Duplicate offence"),
        ("case_invalid_duplicate_urn_used", "Invalid Case: Duplicate URN already used (sent)"),
        ("case_invalid_no_offences", "Invalid Case: No offences"),
        ("result_invalid_duplicate_urn_used", "Invalid Result: Duplicate URN already used (sent)"),
        ("case_invalid_invalid_date", "Invalid Case: Invalid date field")
    )
    IGNORED_CASE_FIELDS = [
        "id",  # Django id is irrelavent
        "auditevent",  # Case is saved before the auditevent so ignore it
        "datavalidation",  # DataValidation objects are defunct
    ]
    IGNORED_RESULT_FIELDS = ["extra_data", "id"]
    IGNORED_FORM_FIELDS = ["id"]
    IGNORED_VALIDATOR_FIELDS = []

    id = models.AutoField(
        primary_key=True,
        verbose_name="Audit Event ID")

    case = models.ForeignKey(
        Case,
        verbose_name="Related case",
        help_text="If there was a successful case loaded then it is related here",
        null=True, blank=True)

    event_type = models.CharField(
        choices=EVENT_TYPE_CHOICES,
        verbose_name="event type",
        help_text="Identified the area of the application that the event happened in",
        max_length=255)

    event_subtype = models.CharField(
        choices=EVENT_SUBTYPE_CHOICES,
        verbose_name="reason for failure",
        help_text="The specific reason for the event",
        max_length=255)

    event_trace = models.CharField(
        max_length=4000,
        verbose_name="error detail",
        help_text="This detail about the reason for this event may be useful for developers to debug import issue",
        blank=True, null=True)

    event_data = HStoreField(
        verbose_name="Event data",
        help_text="If there was a failure and data fields were found, they are stored here to debug",
        null=True, blank=True)

    event_datetime = models.DateTimeField(
        verbose_name="event date and time",
        help_text="The time at which the event occurred",
        auto_now_add=True)

    @property
    def urn(self):
        """URN may come from the case or the extra data. Used in the admin."""
        extra_urn = case_urn = None

        if hasattr(self, "extra_data"):
            if "urn" in self.extra_data:
                extra_urn = self.extra_data["urn"]

        if hasattr(self, "case"):
            if hasattr(self.case, "urn"):
                case_urn = self.case.urn

        if case_urn != extra_urn:
            return "CONFLICTED"
        else:
            return case_urn or extra_urn

    @property
    def initiation_type(self):
        """May come from the case or the event data. Used in the admin"""
        itype_edata = itype_attr = None

        if hasattr(self, "extra_data"):
            if "initiation_type" in self.extra_data:
                itype_edata = self.extra_data["initiation_type"]

        if hasattr(self, "case"):
            if hasattr(self.case, "initiation_type"):
                itype_attr = [
                    i[1]
                    for i in INITIATION_TYPE_CHOICES
                    if self.case.initiation_type == i[0]
                ][0]

        if itype_attr != itype_edata:
            return "CONFLICTED"
        else:
            return itype_attr or itype_edata

    def _get_initiation_type_choice(self):
        for initiation_type in INITIATION_TYPE_CHOICES:
            try:
                if initiation_type[0] == self.case.initiation_type:
                    return initiation_type
            except AttributeError:
                pass

    def populate(self, *args, **kwargs):
        """
        TODO: Visitor pattern made sense when I started this work, not as much anymore
        """

        # TODO: move validation into validators, share them between API, form and admin
        # TODO: refactor clunky field checks
        try:
            if kwargs["event_type"] not in [
                    i[0]
                    for i in self.EVENT_TYPE_CHOICES]:
                raise AuditEventException("Invalid event_type when saving audit event")
        except KeyError:
            raise AuditEventException("Missing event_type when saving audit event")
        else:
            self.event_type = [
                i[0]
                for i in self.EVENT_TYPE_CHOICES
                if i[0] == kwargs["event_type"]][0]

        try:
            if kwargs["event_subtype"] not in [
                    i[0]
                    for i in self.EVENT_SUBTYPE_CHOICES]:
                raise AuditEventException("Invalid event_subtype when saving audit event")
        except KeyError:
            raise AuditEventException("Missing event_subtype when saving audit event")
        else:
            self.event_subtype = [
                i[0]
                for i in self.EVENT_SUBTYPE_CHOICES
                if i[0] == kwargs["event_subtype"]][0]

        self.event_data = kwargs["event_data"] \
            if "event_data" in kwargs \
            else ""
        self.event_trace = kwargs["event_trace"] \
            if "event_trace" in kwargs \
            else ""
        self.event_datetime = kwargs["event_datetime"] \
            if "event_datetime" in kwargs \
            else self.event_datetime

        # If there's a Case floating about, let's copy its details
        if "case" in kwargs:
            case = kwargs["case"]
            if not issubclass(case.__class__, Case):
                raise AuditEventException(
                    "The case kwarg is not a Case object when saving audit event")
            self.case = case

            # Copy the fields of interest
            for field in case._meta.get_fields():
                if field.name not in self.IGNORED_CASE_FIELDS:
                    if hasattr(field, 'name') and hasattr(field, "value"):
                        if field.name != "extra_data":
                            self.event_data[field.name] = field.value

        # If there's a Result floating around, let's copy its details
        if "result" in kwargs:
            result = kwargs["result"]
            if not issubclass(result, Result):
                raise AuditEventException(
                    "The 'result' kwarg is not a Result object when saving audit event")

            # Copy the fields of interest
            fieldnames = result._meta.get_all_filed_names()
            for fieldname in fieldnames:
                field = getattr(result, fieldname)
                if field.name not in self.IGNORED_RESULT_FIELDS:
                    self.event_data[field.name] = field.value

        # If there's a form floating about, let's copy its fields
        elif "form" in kwargs:
            self.event_subtype = "form"
            for k, v in kwargs.items():
                if k not in self.IGNORED_FORM_FIELDS:
                    self.event_data[k] = v

        # If this was just a validator we might have useful kwargs
        elif "validator" in kwargs:
            self.event_subtype = "validator"
            self.event_data = {}
            for k, v in kwargs.items():
                if k not in self.IGNORED_VALIDATOR_FIELDS:
                    self.event_data[k] = v

        self.event_trace = kwargs["event_trace"] \
            if "event_trace" in kwargs \
            else ""

        self.save()

        return self


class CaseTrackerManager(models.Manager):

    def update_stage_for_urn(self, urn, stage):
        try:
            case = Case.objects.get(urn=urn)
            ct, _ = self.all().get_or_create(case=case)
            ct.update_stage(stage)
            ct.save()
        except (Case.DoesNotExist, Case.MultipleObjectsReturned):
            pass


class CaseTracker(models.Model):
    case = models.ForeignKey(Case, null=True)
    last_update = models.DateTimeField(null=True)
    authentication = models.BooleanField(default=False)
    details = models.BooleanField(default=False)
    plea = models.BooleanField(default=False)
    company_finances = models.BooleanField(default=False)
    income_base = models.BooleanField(default=False)
    your_status = models.BooleanField(default=False)
    your_self_employment = models.BooleanField(default=False)
    your_out_of_work_benefits = models.BooleanField(default=False)
    about_your_income = models.BooleanField(default=False)
    your_benefits = models.BooleanField(default=False)
    your_pension_credits = models.BooleanField(default=False)
    your_income = models.BooleanField(default=False)
    hardship = models.BooleanField(default=False)
    household_expenses = models.BooleanField(default=False)
    other_expenses = models.BooleanField(default=False)
    review = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    objects = CaseTrackerManager()

    stage_class_mapping = {"AuthenticationStage": 'authentication',
                           "YourDetailsStage": 'details',
                           "CompanyDetailsStage": 'details',
                           "PleaStage": 'plea',
                           "YourStatusStage": 'your_status',
                           "YourEmploymentStage": 'your_self_employment',
                           "YourSelfEmploymentStage": 'your_self_employment',
                           "YourOutOfWorkBenefitsStage": 'your_out_of_work_benefits',
                           "AboutYourIncomeStage": 'about_your_income',
                           "YourBenefitsStage": 'your_benefits',
                           "YourPensionCreditStage": 'your_pension_credits',
                           "YourIncomeStage": 'your_income',
                           "HardshipStage": 'hardship',
                           "HouseholdExpensesStage": 'household_expenses',
                           "OtherExpensesStage": 'other_expenses',
                           "ReviewStage": 'review',
                           "CompleteStage": 'complete'}

    def get_field_name(self, stage_name):
        return self.stage_class_mapping[stage_name] if stage_name in self.stage_class_mapping else None

    def update_stage(self, stage_name):
        if self.get_field_name(stage_name):
            setattr(self, self.get_field_name(stage_name), True)
            self.last_update = dt.datetime.now()
            self.save()

    def get_stage(self, stage_name):
        return getattr(self, self.get_field_name(stage_name)) if self.get_field_name(stage_name) else None
