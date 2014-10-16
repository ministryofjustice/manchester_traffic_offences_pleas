from dateutil import parser
import logging
import json
import smtplib
import socket

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from apps.govuk_utils.email import TemplateAttachmentEmail
from .models import CourtEmailPlea, CourtEmailCount


logger = logging.getLogger(__name__)


def send_user_confirmation_email(context_data):
    """
    Dispatch an email to the user to confirm that their plea submission
    was successful.
    """

    data = {
        'email': context_data['your_details']['email'],
        'urn': context_data['case']['urn']
    }

    user_email = TemplateAttachmentEmail(
        settings.PLEA_CONFIRMATION_EMAIL_FROM,
        "plea_details.html",
        "plea/plea_email_confirmation.html",
        data,
        "text/html")

    body = render_to_string("plea/plea_email_confirmation.txt", data)

    try:
        user_email.send([data['email'], ],
                        settings.PLEA_CONFIRMATION_EMAIL_SUBJECT.format(**data),
                        body)

    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        logger.error("Error sending email: {0}".format(e.message))

    return True


def send_plea_email(context_data, plea_email_to=None):
    """
    Sends a plea email. All addresses, content etc. are defined in
    settings.

    context_data: dict populated by form fields
    """
    if plea_email_to is None:
        plea_email_to = settings.PLEA_EMAIL_TO

    plea_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                         settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                         settings.PLEA_EMAIL_TEMPLATE,
                                         context_data,
                                         "text/html")

    plp_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                        settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                        settings.PLP_EMAIL_TEMPLATE,
                                        context_data,
                                        "text/html")

    # add DOH / name to the email subject for compliance with the current format
    if isinstance(context_data["case"]["date_of_hearing"], basestring):
        date_of_hearing = parser.parse(context_data["case"]["date_of_hearing"])
    else:
        date_of_hearing = context_data["case"]["date_of_hearing"]
    names = [context_data["your_details"]["name"].rsplit(" ", 1)[-1].upper()]
    first_names = " ".join(context_data["your_details"]["name"].rsplit(" ", 1)[:-1])
    if first_names:
        names.append(first_names)

    context_data["email_name"] = " ".join(names)
    context_data["email_date_of_hearing"] = date_of_hearing.strftime("%Y-%m-%d")

    email_audit = CourtEmailPlea()
    email_audit.urn = context_data["case"]["urn"].upper()
    email_audit.process_form_data(context_data)
    email_audit.address_from = settings.PLEA_EMAIL_FROM
    email_audit.address_to = settings.PLEA_EMAIL_TO
    email_audit.attachment_text = plea_email.attachment_content
    email_audit.body_text = settings.PLEA_EMAIL_BODY
    email_audit.subject = settings.PLEA_EMAIL_SUBJECT.format(**context_data)
    email_audit.status = "created_not_sent"
    email_audit.hearing_date = "{0} {1}".format(context_data["case"]["date_of_hearing"],
                                                context_data["case"]["time_of_hearing"])
    email_audit.save()

    email_count = CourtEmailCount()
    email_count.get_from_context(context_data)
    email_count.save()

    try:
        plea_email.send(plea_email_to,
                        settings.PLEA_EMAIL_SUBJECT.format(**context_data),
                        settings.PLEA_EMAIL_BODY,
                        route="GSI")
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        email_audit.status = "network_error"
        email_audit.status_info = unicode(e)
        email_audit.save()
        return False

    email_audit.status = "sent"
    email_audit.save()

    email_body = "<<<makeaplea-ref: {}/{}>>>".format(email_audit.id, email_count.id)

    try:
        plp_email.send(settings.PLP_EMAIL_TO,
                       settings.PLP_EMAIL_SUBJECT.format(**context_data),
                       email_body,
                       route="GSI")
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        logger.error("Error sending email: {0}".format(e.message))

    # send a user confirmation email after other processing has completed
    if getattr(settings, "SEND_PLEA_CONFIRMATION_EMAIL", False):
        send_user_confirmation_email(context_data)

    return True