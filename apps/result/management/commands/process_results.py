# coding=utf-8
from io import StringIO
import datetime as dt
import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import translation
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from apps.result.models import Result
from apps.plea.models import Court

from dateutil.parser import parse


class Command(BaseCommand):
    help = "Send out result emails"

    def __init__(self, *args, **kwargs):

        super(Command, self).__init__(*args, **kwargs)

        # we want to capture the output of the handle command
        self._log_output = StringIO()

    def log(self, message):
        self.stdout.write(message)
        self._log_output.write(message+"\n")

    def mark_done(self, result, dry_run=False, message=None, sent=False):

        if message:
            self.log(message)

        if not dry_run:
            result.processed = True
            if sent:
                result.sent = True
                result.sent_on = dt.datetime.now()
            result.save()

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Don't send user emails or update result status")

        parser.add_argument(
            "--override-recipient",
            dest="override_recipient",
            default="",
            help=
            "Send a status email to a comma separated list of email addresses, "
            "instead of the user. Combine with --dry-run=True to receive test "
            "resulting emails without changing the database, or emailing the user"
        )

        parser.add_argument(
            "--send-status-email-to",
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

    @staticmethod
    def email_user(data, recipients, lang="en"):

        translation.activate(lang)

        text_template = get_template("emails/user_resulting.txt")
        html_template = get_template("emails/user_resulting.html")

        t_output = text_template.render(data)
        h_output = html_template.render(data)

        connection = get_connection(host=settings.EMAIL_HOST,
                                    port=settings.EMAIL_PORT,
                                    username=settings.EMAIL_HOST_USER,
                                    password=settings.EMAIL_HOST_PASSWORD,
                                    use_tls=settings.EMAIL_USE_TLS)

        subject = _("Make a plea result")

        email = EmailMultiAlternatives(subject, t_output,
                                       settings.PLEA_CONFIRMATION_EMAIL_FROM,
                                       recipients, connection=connection)

        email.attach_alternative(h_output, "text/html")

        email.send(fail_silently=False)

    def get_result_data(self, case, result):
        data = dict(urn=result.urn)

        data["fines"], data["endorsements"], data["total"] = result.get_offence_totals()

        # If we move to using OU codes in Case data this should be replaced by a lookup using the
        # Case OU code
        data["court"] = Court.objects.get_court(result.urn, ou_code=case.ou_code)

        if not data["court"]:
            self.log("URN failed to standardise: {}".format(result.urn))

        data["name"] = case.get_users_name()
        data["pay_by"] = result.pay_by_date
        data["payment_details"] = {"division": result.division,
                                   "account_number": result.account_number}

        return data

    def handle(self, *args, **options):
        resulted_count, not_resulted_count = 0, 0

        if options["override_recipient"]:
            override_recipient = options["override_recipient"].split(",")
        else:
            override_recipient = None

        if options["date"]:
            filter_date = parse(options["date"]).date()
        else:
            filter_date = dt.date.today()

        filter_date_range = (dt.datetime.combine(filter_date, dt.time.min),
                             dt.datetime.combine(filter_date, dt.time.max))

        self.log("Processing results that were imported on {}".format(
            filter_date.strftime("%d/%m/%Y")))

        for result in Result.objects.filter(processed=False,
                                            sent=False,
                                            created__range=filter_date_range):

            can_result, reason = result.can_result()

            case = result.get_associated_case()
            if not case:

                self.mark_done(result, dry_run=options["dry_run"])

                not_resulted_count += 1
                continue

            if not can_result:

                self.mark_done(result, dry_run=options["dry_run"],
                               message="Skipping {} because {}".format(result.urn, reason))

                not_resulted_count += 1
                continue

            data = self.get_result_data(case, result)

            if override_recipient:
                self.email_user(data, override_recipient)

            elif not options["dry_run"]:
                self.email_user(data, [case.email], case.language)

            self.mark_done(result, sent=True, dry_run=options["dry_run"],
                           message="Completed case {} email sent to {}".format(case.urn, case.email))

            resulted_count += 1

        self.log("total resulted: {}\ntotal not resulted: {}".format(resulted_count, not_resulted_count))

        if options["status_email_recipients"]:
            recipients = options["status_email_recipients"].split(",")

            env = os.environ.get('ENV', '<ENV>')

            send_mail('[{}] make-a-plea resulting status email'.format(env),
                      self._log_output.getvalue(),
                      settings.PLEA_EMAIL_FROM,
                      recipients, fail_silently=False)
