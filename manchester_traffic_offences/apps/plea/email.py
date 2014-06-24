from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


class TemplateAttachmentEmail(object):
    """
    Email with a templated attachment.
    """
    def __init__(self, from_address, attachment_name, attachment_template,
                 attachment_data, attachment_mime):
        self.from_address = from_address
        self.attachment_name = attachment_name
        self.attachment_template = attachment_template
        self.attachment_data = attachment_data
        self.attachment_mime = attachment_mime

    def send(self, to_address, subject, body):
        attachment_content = render_to_string(self.attachment_template,
                                              self.attachment_data)

        email = EmailMessage(subject, body, self.from_address,
                             to_address)
        email.attach(self.attachment_name, attachment_content,
                     self.attachment_mime)
        email.send(fail_silently=False)


def send_plea_email(context_data):
    """
    Sends a plea email. All addresses, content etc. are defined in
    settings.

    context_data: dict populated by form  fields
    """
    plea_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                         settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                         settings.PLEA_EMAIL_TEMPLATE,
                                         context_data,
                                         "text/html")
    plea_email.send((settings.PLEA_EMAIL_TO, ),
                    settings.PLEA_EMAIL_SUBJECT.format(**context_data),
                    settings.PLEA_EMAIL_BODY)