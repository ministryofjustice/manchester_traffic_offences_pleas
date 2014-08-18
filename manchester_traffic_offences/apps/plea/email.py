import smtplib
import socket

from django.conf import settings

from govuk_utils.email import TemplateAttachmentEmail
from .models import CourtEmailPlea, CourtEmailCount


def send_plea_email(context_data, plea_email_to=settings.PLEA_EMAIL_TO):
    """
    Sends a plea email. All addresses, content etc. are defined in
    settings.

    context_data: dict populated by form fields
    """
    plea_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                         settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                         settings.PLEA_EMAIL_TEMPLATE,
                                         context_data,
                                         "text/html")

    email_audit = CourtEmailPlea()
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

    try:
        plea_email.send(plea_email_to,
                        settings.PLEA_EMAIL_SUBJECT.format(**context_data),
                        settings.PLEA_EMAIL_BODY)
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        email_audit.status = "network_error"
        email_audit.status_info = unicode(e)
        email_audit.save()
        return False

    email_audit.status = "sent"
    email_audit.save()

    email_count = CourtEmailCount()
    email_count.get_from_context(context_data)
    email_count.save()

    return True
