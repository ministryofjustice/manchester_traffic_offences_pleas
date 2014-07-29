from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string


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
