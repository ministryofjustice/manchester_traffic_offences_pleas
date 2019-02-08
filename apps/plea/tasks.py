from __future__ import absolute_import

import logging
import smtplib
import socket
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.conf import settings
from django.utils import translation

from apps.plea.attachment import TemplateAttachmentEmail

from celery import shared_task

from apps.plea.models import Case, CourtEmailCount, Court
from apps.plea.standardisers import format_for_region

logger = logging.getLogger(__name__)


def get_email_subject(email_data):
    if email_data["notice_type"]["sjp"] is True:
        subject = "ONLINE PLEA: {case[formatted_urn]} <SJP> {email_name}"
    else:
        subject = "ONLINE PLEA: {case[formatted_urn]} DOH: {email_date_of_hearing} {email_name}"

    email_data["case"]["formatted_urn"] = format_for_region(email_data["case"]["urn"])
    return subject.format(**email_data)


def get_court(urn, ou_code):
    try:
        court_obj = Court.objects.get_court(urn, ou_code=ou_code)
    except Court.DoesNotExist:
        logger.warning("URN does not have a matching Court entry: {}".format(urn))
        raise
    return court_obj


def is_18_or_under(date_of_birth):
    if not isinstance(date_of_birth, date):
        return False

    target_date = (datetime.today() - relativedelta(years=18)).date()

    return date_of_birth >= target_date


def get_smtp_gateway(email_address):
    if email_address.endswith('gsi.gov.uk'):
        return "GSI"
    return "PUB"


@shared_task(bind=True, max_retries=10, default_retry_delay=900)
def email_send_court(self, case_id, count_id, email_data):
    email_data["urn"] = format_for_region(email_data["case"]["urn"])

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)

    court_obj = get_court(email_data["case"]["urn"], case.ou_code)

    plea_email_to = [court_obj.submission_email]
    smtp_route = get_smtp_gateway(court_obj.submission_email)

    email_count = None
    if not court_obj.test_mode:
        email_count = CourtEmailCount.objects.get(pk=count_id)

    case.add_action("Court email started", "")

    email_subject = get_email_subject(email_data)
    email_body = "<<<makeaplea-ref: {}/{}>>>".format(case.id, count_id)

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
        logger.warning("Error sending email to court: {0}".format(exc))
        case.add_action("Court email network error", u"{}: {}".format(type(exc), exc))
        if email_count is not None:
            email_count.get_status_from_case(case)
            email_count.save()
        case.sent = False
        case.save()

        raise self.retry(args=[case_id, count_id, email_data], exc=exc)

    case.add_action("Court email sent", "Sent mail to {0} via {1}".format(plea_email_to, smtp_route))

    if not court_obj.test_mode:
        case.sent = True
        case.save()

        email_count.get_status_from_case(case)
        email_count.save()

    return True


@shared_task(bind=True, max_retries=10, default_retry_delay=1800)
def email_send_prosecutor(self, case_id, email_data):
    smtp_route = "PNN"

    email_data["urn"] = format_for_region(email_data["case"]["urn"])

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)

    court_obj = get_court(email_data["case"]["urn"], case.ou_code)

    case.add_action("Prosecutor email started", "")

    email_subject = "POLICE " + get_email_subject(email_data)
    email_body = ""

    email_data["your_details"]["18_or_under"] = is_18_or_under(
        email_data["your_details"].get("date_of_birth"))

    plp_email = TemplateAttachmentEmail(settings.PLP_EMAIL_FROM,
                                        settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                        "emails/attachments/plp_email.html",
                                        email_data,
                                        "text/html")

    if court_obj.plp_email:
        try:
            with translation.override("en"):
                plp_email.send([court_obj.plp_email],
                               email_subject,
                               email_body,
                               route=smtp_route)
        except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
            logger.warning("Error sending email to prosecutor: {0}".format(exc))
            case.add_action("Prosecutor email network error", u"{}: {}".format(type(exc), exc))
            raise self.retry(args=[case_id, email_data], exc=exc)

        case.add_action("Prosecutor email sent", "Sent mail to {0} via {1}".format(court_obj.plp_email, smtp_route))

    else:
        case.add_action("Prosecutor email not sent", "No plp email in court data")

    return True


@shared_task(bind=True, max_retries=10, default_retry_delay=1800)
def email_send_user(self, case_id, email_address, subject, html_body, txt_body):
    """
    Dispatch an email to the user to confirm that their plea submission
    was successful.
    """

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(id=case_id)
    case.add_action("User email started", "")

    connection = get_connection(host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username=settings.EMAIL_HOST_USER,
                                password=settings.EMAIL_HOST_PASSWORD,
                                use_tls=settings.EMAIL_USE_TLS)

    email = EmailMultiAlternatives(subject, txt_body, settings.PLEA_CONFIRMATION_EMAIL_FROM,
                                   [email_address], connection=connection)

    email.attach_alternative(html_body, "text/html")

    try:
        email.send(fail_silently=False)
    except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
        logger.warning("Error sending user confirmation email: {0}".format(exc))
        case.add_action("User email network error", u"{}: {}".format(type(exc), exc))
        raise self.retry(args=[case_id, email_address, subject, html_body, txt_body], exc=exc)

    case.add_action("User email sent", "")

    return True
