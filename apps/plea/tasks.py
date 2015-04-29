from __future__ import absolute_import

from dateutil import parser
import logging
import json
import smtplib
import socket

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.conf import settings
from django.template.loader import render_to_string

from apps.govuk_utils.email import TemplateAttachmentEmail

from manchester_traffic_offences.celery import app
from apps.plea.models import Case, CourtEmailCount, Court

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=5, default_retry_delay=10)
def email_send_court(self, case_id, count_id, email_data):
    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)

    try:
        court_obj = Court.objects.get_by_urn(email_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.error("URN does not have a matching Court entry: {}".format(
            email_data["case"]["urn"]))
        raise

    plea_email_to = [court_obj.submission_email]

    email_count = None
    if not court_obj.test_mode:
        email_count = CourtEmailCount.objects.get(pk=count_id)

    case.add_action("Court email started", "")

    email_body = "<<<makeaplea-ref: {}/{}>>>".format(case.id, count_id)

    plea_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                         settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                         settings.PLEA_EMAIL_TEMPLATE,
                                         email_data,
                                         "text/html")

    try:
        plea_email.send(plea_email_to,
                        settings.PLEA_EMAIL_SUBJECT.format(**email_data),
                        email_body,
                        route="GSI")
    except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
        logger.error("Error sending email to court: {0}".format(exc))
        case.add_action("Court email network error", unicode(exc))
        email_count.get_status_from_case(case)
        email_count.save()
        case.sent = False
        case.save()

        raise self.retry(exc=exc)

    case.add_action("Court email sent", "")

    if not court_obj.test_mode:
        email_count.get_status_from_case(case)
        email_count.save()

    if court_obj.plp_email:
        email_send_prosecutor.delay(email_data, case_id)

    email_send_user.delay(email_data, case_id)


@app.task(bind=True)
def email_send_prosecutor(self, email_data, case_id):
    try:
        court_obj = Court.objects.get_by_urn(email_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.error("URN does not have a matching Court entry: {}".format(
            email_data["case"]["urn"]))
        raise

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)
    case.add_action("Prosecutor email started", "")

    plp_email = TemplateAttachmentEmail(settings.PLP_EMAIL_FROM,
                                        settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                        settings.PLP_EMAIL_TEMPLATE,
                                        email_data,
                                        "text/html")
    if court_obj.plp_email:
        try:
            plp_email.send([court_obj.plp_email],
                           settings.PLP_EMAIL_SUBJECT.format(**email_data),
                           settings.PLEA_EMAIL_BODY,
                           route="GSI")
        except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
            logger.error("Error sending email to prosecutor: {0}".format(exc))
            case.add_action("Prosecutor email network error", unicode(exc))
            raise self.retry(email_data, exc=exc)

        case.add_action("Prosecutor email sent", "")
    else:
        case.add_action("Prosecutor email not sent", "No plp email in court data")

    return True


@app.task(bind=True)
def email_send_user(self, email_data, case_id):
    """
    Dispatch an email to the user to confirm that their plea submission
    was successful.
    """
    # No error trapping, let these fail hard if the objects can't be found
    from .stages import get_plea_type

    if email_data['case']['plea_made_by'] == "Defendant":
        email = email_data['your_details']['email']
        name = email_data['your_details']['name']
    else:
        email = email_data['company_details']['email']
        name = email_data['company_details']['name']

    try:
        court_obj = Court.objects.get_by_urn(email_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.error("URN does not have a matching Court entry: {}".format(
            email_data["case"]["urn"]))
        raise

    data = {
        'email': email,
        'urn': email_data['case']['urn'],
        'plea_made_by': email_data['case']['plea_made_by'],
        'number_of_charges': email_data['case']['number_of_charges'],
        'plea_type': get_plea_type(email_data),
        'name': name,
        'court_address': court_obj.court_address,
        'court_email': court_obj.court_email
    }

    case = Case.objects.get(pk=case_id)
    case.add_action("User email started", "")

    html_body = render_to_string("plea/plea_email_confirmation.html", data)
    txt_body = render_to_string("plea/plea_email_confirmation.txt", data)

    subject = settings.PLEA_CONFIRMATION_EMAIL_SUBJECT.format(**data)

    connection = get_connection(host=settings.USER_SMTP_EMAIL_HOST,
                                port=settings.USER_SMTP_EMAIL_PORT,
                                username=settings.USER_SMTP_EMAIL_HOST_USERNAME,
                                password=settings.USER_SMTP_EMAIL_HOST_PASSWORD,
                                use_tls=True)

    email = EmailMultiAlternatives(
        subject, txt_body, settings.PLEA_CONFIRMATION_EMAIL_FROM,
        [data['email']], connection=connection)

    email.attach_alternative(html_body, "text/html")

    try:
        email.send(fail_silently=False)
    except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
        logger.error("Error sending user confirmation email: {0}".format(exc))
        case.add_action("Prosecutor email network error", unicode(exc))
        self.retry(email_data, exc=exc)

    case.add_action("User email sent", "")

    return True