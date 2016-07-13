# coding=utf-8
import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.plea.models import Court, Case

from dateutil.parser import parse


class Command(BaseCommand):

    def _get_date_range(self, fld_name, date):

        return {
            "{}__gte".format(fld_name):
                dt.datetime.combine(date, dt.time.min),
            "{}__lte".format(fld_name):
                dt.datetime.combine(date, dt.time.max)
        }

    def handle(self, *args, **options):

        date = dt.datetime.today() - dt.timedelta(1)

        court_data = []

        for court in Court.objects.filter(enabled=True):

            data = self._get_stats(court, date)

            court_data.append(
                (court.id, data),
            )

        print court_data

    def _get_stats(self, court, date):

        created_date_range = self._get_date_range("created", date)
        completed_on_date_range = self._get_date_range("completed_on", date)

        # number of entries imported from the soap gateway
        imported_count = Case.objects.filter(
            imported=True, **created_date_range).count()

        # number of completed submissions
        submission_count = Case.objects.filter(
            **completed_on_date_range).count()

        # number of unvalidated submissions
        unvalidated_count = Case.objects.filter(
            imported=False, **completed_on_date_range).count()

        # number of failed email sending situations
        email_failure_count = Case.objects.filter(
            sent=False, **completed_on_date_range).count()

        # number of sjp cases
        sjp_count = Case.objects.fiter(initiation_type="J",
                                       **created_date_range).count()

        return dict(
            imported=imported_count,
            submissions=submission_count,
            unvalidated_submissions=unvalidated_count,
            email_failure=email_failure_count,
            sjp_count=sjp_count
        )

        # soap gateway import metrics
        # total imported cases
        # total failed imports
        #    - duplicate case number
        #    - invalid case initiation type
        #    - invalid URN


