# coding=utf-8
import cStringIO as StringIO
from collections import OrderedDict
import csv
import datetime as dt

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand

from apps.result.models import Result
from apps.plea.models import Court

from dateutil.parser import parse


class Command(BaseCommand):
    help = "Send out result emails"

    def __init__(self, *args, **kwargs):

        super(Command, self).__init__(*args, **kwargs)

        # we want to capture the output of the handle command
        self._data = StringIO.StringIO()
        self._csv = csv.writer(self._data, dialect="excel")

    def add_arguments(self, parser):

        parser.add_argument(
            "--send-email-to",
            dest="status_email_recipients",
            default="",
            help="A comma separate list of email recipients to receive the status email. "
                 "If blank, then output will be sent to stdout"
        )

        parser.add_argument(
            "--date",
            dest="date",
            default="",
            help="The date to process results - uses the created timestamp of the Result model. "
                 "If not specified the script will default to today"
        )

        parser.add_argument(
            "--show-all",
            action="store_true",
            dest="show_all",
            default=False,
            help="Show all results including processed results")

    @staticmethod
    def get_result_data(case, result):
        data = OrderedDict()

        data["name"] = case.get_users_name()
        data["case_number"] = case.case_number
        data["urn"] = result.urn
        data["ou_code"] = case.ou_code
        data["court"] = Court.objects.get_court(result.urn, ou_code=case.ou_code).court_name
        data["fines"], data["endorsements"], data["total"] = result.get_offence_totals()

        data["fines"] = " / ".join(data["fines"])
        data["endorsements"] = " / ".join(data["endorsements"])

        data["pay_by"] = result.pay_by_date
        data["division"] = result.division[0],
        data["account_number"] = result.account_number

        return data

    def csv_write_header(self):
        self._csv.writerow([
            "name",
            "case number",
            "urn",
            "OU code",
            "court",
            "fines",
            "endorsements",
            "total",
            "pay by",
            "division code",
            "account number"
        ])

    def send_status_email(self, recipients):
        date_str = dt.date.today().strftime("%Y-%m-%d")

        message = EmailMessage(
            'Resulting CSV {}'.format(date_str),
            '',
            settings.PLEA_EMAIL_FROM,
            recipients)

        message.attach('result-{}-data.csv'.format(date_str),
                       self._data.read(),
                       "text/csv")
        message.send()

    def handle(self, *args, **options):

        if options["date"]:
            filter_date = parse(options["date"]).date()
        else:
            filter_date = dt.date.today()

        filter_date_range = (dt.datetime.combine(filter_date, dt.time.min),
                             dt.datetime.combine(filter_date, dt.time.max))

        print "Processing results that were imported on {}".format(
            filter_date.strftime("%d/%m/%Y"))

        self.csv_write_header()

        results = Result.objects.filter(
            processed=False, created__range=filter_date_range)

        if not options["show_all"]:
            results.filter(sent=False)

        for result in results:

            can_result, _ = result.can_result()

            case = result.get_associated_case()

            if can_result and case:

                data = self.get_result_data(case, result)

                self._csv.writerow(data.values())

        recipients = options["status_email_recipients"].split(",")

        self._data.reset()

        if recipients != ['']:
            self.send_status_email(recipients)
        else:
            print self._data.read()
