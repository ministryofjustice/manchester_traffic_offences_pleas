from collections import OrderedDict
import datetime as dt
import operator
from functools import reduce
from django.views.generic.base import TemplateView
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.plea.models import Case, Court


FIELD_NAMES = OrderedDict([
    ("imported", "SOAP gateway cases imported"),
    ("submissions",	"user submissions"),
    ("unvalidated_submissions", "unvalidated submissions"),
    ("email_failure", "submission emails failures"),
    ("sjp_count", "SJP submissions")])


class CourtDataView(TemplateView):
    template_name = "monitoring/court_data.html"

    @method_decorator(staff_member_required)
    @method_decorator(cache_page(60*60*24))
    def dispatch(self, *args, **kwargs):
        return super(CourtDataView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourtDataView, self).get_context_data(**kwargs)

        today = dt.date.today()

        data = []

        courts = Court.objects.filter(enabled=True)

        for i in range(1, 30):
            date = today - dt.timedelta(i)

            data.append({
                "date": date.strftime("%a %d %b %y"),
                "data": [self._get_stats(court, date) for court in courts]
            })

        context["data"] = data
        context["courts"] = courts

        return context

    @staticmethod
    def _get_date_range(fld_name, date):

        return {
            "{}__gte".format(fld_name):
                dt.datetime.combine(date, dt.time.min),
            "{}__lte".format(fld_name):
                dt.datetime.combine(date, dt.time.max)
        }

    @staticmethod
    def _get_ou_code_query(ou_codes):
        return reduce(
            operator.or_,
            [Q(ou_code__startswith=elem.ou_code) for elem in ou_codes])

    @staticmethod
    def _analyse_data(data):
        """
        Initially we're performing a superficial analysis of data - e.g. if
        email sending failures then display an error, if we have no
        submissions display a warning etc.

        Depending on user feedback, a future iteration may involve a more
        sophisticated analysis - maybe using some statistical methods such as
        moving averages to try to flag potential failures such as low
        submissions for a particular court based on previous performance, but
        taking into consideration that activity may be low during certain
        periods (weekends, holidays, etc.)
        """

        for field in data.keys():
            if field == "imported":
                if data[field]["value"] == 0:
                    data[field]["status"] = "warn"

            if field == "submissions":
                if data[field]["value"] == 0:
                    data[field]["status"] = "warn"

            if field == "email_failure":
                if data[field]["value"] > 0:
                    data[field]["status"] = "error"

            if field == "unvalidated_submissions":
                if data[field]["value"] > 0:
                    data[field]["status"] = "info"

        return data

    def _get_stats(self, court, date):

        created_date_range = self._get_date_range("created", date)
        completed_on_date_range = self._get_date_range("completed_on", date)

        cases = Case.objects.filter(urn__startswith=court.region_code)

        if court.oucode_set.count():
            cases = cases.filter(self._get_ou_code_query(court.oucode_set.all()))

        # number of entries imported from the soap gateway
        imported_count = cases.filter(
            imported=True,
            **created_date_range).count()

        # number of completed submissions
        submission_count = cases.filter(
            **completed_on_date_range).count()

        # number of unvalidated submissions
        unvalidated_count = cases.filter(
            imported=False, **completed_on_date_range).count()

        # number of failed email sending situations
        email_failure_count = cases.filter(
            sent=False, **completed_on_date_range).count()

        # number of sjp cases
        sjp_count = cases.filter(
            initiation_type="J",
            **created_date_range).count()

        data = OrderedDict((
            ("imported", {"value": imported_count,
                          "status": ""}),
            ("submissions", {"value": submission_count,
                             "status": ""}),
            ("unvalidated_submissions", {"value": unvalidated_count,
                                         "status": ""}),
            ("email_failure", {"value": email_failure_count,
                               "status": ""}),
            ("sjp_count", {"value": sjp_count,
                           "status": ""})))

        return self._analyse_data(data)

        # Additional metrics which could be reported:
        # soap gateway import metrics
        # total imported cases
        # total failed imports
        #    - duplicate case number
        #    - invalid case initiation type
        #    - invalid URN
        #    - total results ingested
        #    - total results emails sent





