import smtplib
import socket

from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from .models import CourtEmailPlea


class TemplateAttachmentEmail(object):
    """
    Email with a templated attachment.
    """
    def __init__(self, from_address, attachment_name, attachment_template,
                 attachment_data, attachment_mime):
        self.email = None
        self.attachment_content = None
        self.from_address = from_address
        self.attachment_name = attachment_name
        self.attachment_template = attachment_template
        self.attachment_data = attachment_data
        self.attachment_mime = attachment_mime

    def send(self, to_address, subject, body):
        self.attachment_content = render_to_string(self.attachment_template,
                                              self.attachment_data)

        self.email = EmailMessage(subject, body, self.from_address,
                                  to_address)
        self.email.attach(self.attachment_name, self.attachment_content,
                          self.attachment_mime)
        self.email.send(fail_silently=False)


def send_plea_email(context_data, plea_email_to=settings.PLEA_EMAIL_TO):
    """
    Sends a plea email. All addresses, content etc. are defined in
    settings.

    context_data: dict populated by form  fields
    """

    email_audit = CourtEmailPlea()
    email_audit.process_form_data(context_data)
    email_audit.address_from = settings.PLEA_EMAIL_FROM
    email_audit.address_to = settings.PLEA_EMAIL_TO
    email_audit.attachment_text = ""
    email_audit.body_text = settings.PLEA_EMAIL_BODY
    email_audit.subject = settings.PLEA_EMAIL_SUBJECT.format(**context_data)
    email_audit.status = "created_not_sent"
    email_audit.save()

    plea_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                         settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                         settings.PLEA_EMAIL_TEMPLATE,
                                         context_data,
                                         "text/html")

    try:
        plea_email.send((plea_email_to, ),
                        settings.PLEA_EMAIL_SUBJECT.format(**context_data),
                        settings.PLEA_EMAIL_BODY)
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        email_audit.status = "network_error"
        email_audit.save()
        return False

    email_audit.status = "sent"
    email_audit.save()

    return True
