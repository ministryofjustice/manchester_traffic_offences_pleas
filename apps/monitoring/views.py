from collections import OrderedDict
import datetime as dt

from django.views.generic.base import TemplateView
from django.contrib.admin.views.decorators import staff_member_required

from apps.plea.models import Case, Court


FIELD_NAMES = OrderedDict([
    ("imported", "Total cases imported from SOAP gateway"),
    ("submissions",	"Total user submissions"),
    ("unvalidated_submissions", "Total user submissions that were unvalidated"),
    ("email_failure", "Total submission emails that were not received by the court"),
    ("sjp_count", "Number of SJP submissions")])


class CourtDataView(TemplateView):
    template_name = "monitoring/court_data.html"

    def get_context_data(self, **kwargs):
        context = super(CourtDataView, self).get_context_data(**kwargs)

        today = dt.date.today()

        data = []

        courts = Court.objects.filter(enabled=True)

        for i in range(1, 30):
            date = today - dt.timedelta(i)

            data.append({
                "date": date,
                "data": self.reorder_for_display(
                    [self._get_stats(court, date) for court in courts])
            })

        context["field_names"] = FIELD_NAMES.values()
        context["data"] = data
        context["courts"] = courts

        return context

    def reorder_for_display(self, row):
        """
        NOTE: reordering the data for html table display rather than
        querying it in the correct format, because I suspect this
        data ultimately will be provided via a rest API, in which
        case the current way it is generated is probably more
        appropriate
        """

        row_data = []

        for field in row[0].keys():
            row_data.append([field]+[data[field] for data in row])

        return row_data

    def _get_date_range(self, fld_name, date):

        return {
            "{}__gte".format(fld_name):
                dt.datetime.combine(date, dt.time.min),
            "{}__lte".format(fld_name):
                dt.datetime.combine(date, dt.time.max)
        }

    def _analyse_data(self, data):
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

        court_query = dict(region_code=court.region_code)

        # number of entries imported from the soap gateway
        imported_count = Case.objects.filter(
            imported=True,
            urn__startswith=court.region_code,
            **created_date_range).count()

        # number of completed submissions
        submission_count = Case.objects.filter(
            urn__startswith=court.region_code,
            **completed_on_date_range).count()

        # number of unvalidated submissions
        unvalidated_count = Case.objects.filter(
            urn__startswith=court.region_code,
            imported=False, **completed_on_date_range).count()

        # number of failed email sending situations
        email_failure_count = Case.objects.filter(
            urn__startswith=court.region_code,
            sent=False, **completed_on_date_range).count()

        # number of sjp cases
        sjp_count = Case.objects.filter(
            urn__startswith=court.region_code,
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

        # Additional metrics which could be recorded from the soap gateway:
        # soap gateway import metrics
        # total imported cases
        # total failed imports
        #    - duplicate case number
        #    - invalid case initiation type
        #    - invalid URN





