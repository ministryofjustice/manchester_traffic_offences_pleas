import json
import re
import smtplib
import socket
import time
import sys
from django.conf import settings

from django.core.management.base import BaseCommand
from django.utils import translation
from apps.plea.attachment import TemplateAttachmentEmail
from apps.plea.models import Court, Case
from apps.plea.tasks import get_email_subject


def manual_send_court_email(json_data, case_id):
    """
    Used to manually send a court email from archieved user data, in case of a email sending
    failure.

    This function is run via the managemnt command:

    ./manage.py resend_court_emails {jsonnfile1} {jsonfile2} etc.

    """

    email_data = json.loads(json_data)

    try:
        case = Case.objects.get(pk=case_id)
    except Case.DoesNotExist:
        case = None

    case_id = case.id if case else "XX"

    smtp_route = "PUB"

    try:
        court_obj = Court.objects.get_by_urn(email_data["case"]["urn"])
    except Court.DoesNotExist:
        raise

    plea_email_to = [court_obj.submission_email]

    email_subject = get_email_subject(email_data)
    email_body = "<<<makeaplea-ref: {}/{}>>>".format(case_id, "XX")

    plea_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                         settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                         "emails/attachments/plea_email.html",
                                         email_data,
                                         "text/html")

    try:
        with translation.override("en"):
            plea_email.send(plea_email_to,
                            email_subject,
                            email_body,
                            route=smtp_route)

    except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
        raise
    else:
        if case:
            case.add_action("Court email sent", "Sent mail to {0} via {1}".format(plea_email_to, smtp_route))
            case.sent = True
            case.save()



class Command(BaseCommand):
    help = "Resend court emails from the archived json file"

    def add_arguments(self, parser):

        parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):

        case_id_re = re.compile(".*\[(\d+)\]")

        for file_ in options["file"]:
            sys.stdout.write("Attempting to process: {}\n".format(file_))

            matches = case_id_re.match(file_)

            if not matches:
                sys.stderr.write("Can't find a case id in file name, skipping\n")
                continue

            case_id = int(matches.groups()[0])

            with open(file_) as fd:
                data = fd.read()

                try:
                    manual_send_court_email(data, case_id)
                except Exception as ex:
                    sys.stderr.write("error: {}\n".format(ex))

                    continue

                sys.stdout.write("success!\n")

            sys.stdout.write("sleeping for 10 seconds...\n")
            time.sleep(10)


