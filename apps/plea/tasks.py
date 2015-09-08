from __future__ import absolute_import

import logging
import smtplib
import socket

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.text import wrap
from django.utils.translation import ugettext_lazy as _

from apps.govuk_utils.email import TemplateAttachmentEmail

from manchester_traffic_offences.celery import app
from apps.plea.models import Case, CourtEmailCount, Court

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=5)
def email_send_court(self, case_id, count_id, email_data):
    smtp_route = "GSI"

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)

    try:
        court_obj = Court.objects.get_by_urn(email_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.warning("URN does not have a matching Court entry: {}".format(
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
                                         "emails/attachments/plea_email.html",
                                         email_data,
                                         "text/html")

    try:
        # with translation.override("en"):
        plea_email.send(plea_email_to,
                        settings.PLEA_EMAIL_SUBJECT.format(**email_data),
                        email_body,
                        route=smtp_route)
    except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
        logger.warning("Error sending email to court: {0}".format(exc))
        case.add_action("Court email network error", unicode(exc))
        if email_count is not None:
            email_count.get_status_from_case(case)
            email_count.save()
        case.sent = False
        case.save()

        raise self.retry(args=[case_id, count_id, email_data], exc=exc)

    case.add_action("Court email sent", "Sent mail to {0} via {1}".format(plea_email_to, smtp_route))

    if not court_obj.test_mode:
        email_count.get_status_from_case(case)
        email_count.save()

    return True


@app.task(bind=True, max_retries=5)
def email_send_prosecutor(self, case_id, email_data):
    smtp_route = "PNN"

    try:
        court_obj = Court.objects.get_by_urn(email_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.warning("URN does not have a matching Court entry: {}".format(
            email_data["case"]["urn"]))
        raise

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)
    case.add_action("Prosecutor email started", "")

    plp_email = TemplateAttachmentEmail(settings.PLP_EMAIL_FROM,
                                        settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                        "emails/attachments/plp_email.html",
                                        email_data,
                                        "text/html")

    if court_obj.plp_email:
        try:
            # with translation.override("en"):
            plp_email.send([court_obj.plp_email],
                           settings.PLP_EMAIL_SUBJECT.format(**email_data),
                           settings.PLEA_EMAIL_BODY,
                           route=smtp_route)
        except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
            logger.warning("Error sending email to prosecutor: {0}".format(exc))
            case.add_action("Prosecutor email network error", unicode(exc))
            raise self.retry(args=[case_id, email_data], exc=exc)

        case.add_action("Prosecutor email sent", "Sent mail to {0} via {1}".format(court_obj.plp_email, smtp_route))

    else:
        case.add_action("Prosecutor email not sent", "No plp email in court data")

    return True


@app.task(bind=True, max_retries=5)
def email_send_user(self, case_id, email_data):
    """
    Dispatch an email to the user to confirm that their plea submission
    was successful.
    """

    # No error trapping, let these fail hard if the objects can't be found

    from .stages import get_plea_type

    email = email_data.get("review", {}).get("email", False)

    case = Case.objects.get(pk=case_id)

    if not email:
        case.add_action("No email entered, user email not sent", "")
        return True

    if email_data['case']['plea_made_by'] == "Defendant":
        first_name = email_data['your_details']['first_name']
        last_name = email_data['your_details']['last_name']
    else:
        first_name = email_data['company_details']['first_name']
        last_name = email_data['company_details']['last_name']

    try:
        court_obj = Court.objects.get_by_urn(email_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.warning("URN does not have a matching Court entry: {}".format(
            email_data["case"]["urn"]))
        raise

    data = {
        'email': email,
        'urn': email_data['case']['urn'],
        'plea_made_by': email_data['case']['plea_made_by'],
        'number_of_charges': email_data['case']['number_of_charges'],
        'plea_type': get_plea_type(email_data),
        'first_name': first_name,
        'last_name': last_name,
        'court_address': court_obj.court_address,
        'court_email': court_obj.court_email
    }

    case.add_action("User email started", "")

    html_body = render_to_string("emails/user_plea_confirmation.html", data)
    txt_body = wrap(render_to_string("emails/user_plea_confirmation.txt", data), 72)

    subject = _("Online plea submission confirmation")

    connection = get_connection(host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username=settings.EMAIL_HOST_USER,
                                password=settings.EMAIL_HOST_PASSWORD,
                                use_tls=settings.EMAIL_USE_TLS)

    email = EmailMultiAlternatives(subject, txt_body, settings.PLEA_CONFIRMATION_EMAIL_FROM,
                                   [data['email']], connection=connection)

    email.attach_alternative(html_body, "text/html")

    try:
        email.send(fail_silently=False)
    except (smtplib.SMTPException, socket.error, socket.gaierror) as exc:
        logger.warning("Error sending user confirmation email: {0}".format(exc))
        case.add_action("User email network error", unicode(exc))
        raise self.retry(args=[case_id, email_data], exc=exc)

    case.add_action("User email sent", "")

    return True
