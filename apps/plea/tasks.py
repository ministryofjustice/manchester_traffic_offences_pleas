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
from apps.plea.models import Case, CourtEmailCount

logger = logging.getLogger(__name__)

@app.task
def email_send_user(email_data):
    """
    Dispatch an email to the user to confirm that their plea submission
    was successful.
    """

    from .stages import get_plea_type

    data = {
        'email': email_data['your_details']['email'],
        'urn': email_data['case']['urn'],
        'number_of_charges': email_data['case']['number_of_charges'],
        'name': email_data['your_details']['name'],
        'plea_type': get_plea_type(email_data)
    }

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
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        logger.error("Error sending user confirmation email: {0}".format(e))

    return True


@app.task
def email_send_court(case_id, count_id, email_data):
    plea_email_result = False
    plea_email_to = settings.PLEA_EMAIL_TO

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)
    email_count = CourtEmailCount.objects.get(pk=count_id)

    email_body = "<<<makeaplea-ref: {}/{}>>>".format(case.id, email_count.id)

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

        case.status = "network_error"
        case.status_info = unicode(exc)
        email_count.get_status_from_case(case)
        email_count.save()
        case.save()

        raise email_send_court.retry(case_id, count_id, exc=exc)

    case.status = "sent"
    case.save()
    email_count.get_status_from_case(case)
    email_count.save()

    email_send_prosecutor.delay(email_data)
    email_send_user.delay(email_data)


@app.task
def email_send_prosecutor(email_data):
    plp_email_to = settings.PLP_EMAIL_TO

    plp_email = TemplateAttachmentEmail(settings.PLP_EMAIL_FROM,
                                        settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                        settings.PLP_EMAIL_TEMPLATE,
                                        email_data,
                                        "text/html")

    try:
        plp_email.send(settings.PLP_EMAIL_TO,
                       settings.PLP_EMAIL_SUBJECT.format(**email_data),
                       settings.PLEA_EMAIL_BODY,
                       route="GSI")
    except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
        logger.error("Error sending email to prosecutor: {0}".format(exc))
        raise email_send_prosecutor.retry(email_data, exc=exc)

    return True