from django.conf import settings
from django.core.mail import get_connection
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

    def send(self, to_address, subject, body, route=None):
        connection = None
        if route:
            route_host = settings.SMTP_ROUTES[route]["HOST"]
            route_port = settings.SMTP_ROUTES[route]["PORT"]
            route_user = settings.SMTP_ROUTES[route].get("USERNAME", '')
            route_password = settings.SMTP_ROUTES[route].get("PASSWORD", '')
            route_use_tls = settings.SMTP_ROUTES[route].get("USE_TLS", True)

            connection = get_connection(host=route_host,
                                        port=route_port,
                                        username=route_user,
                                        password=route_password,
                                        use_tls=route_use_tls)

        self.attachment_content = render_to_string(self.attachment_template,
                                                   self.attachment_data)
        if connection:
            self.email = EmailMessage(subject, body, self.from_address,
                                      to_address, connection=connection)
        else:
            self.email = EmailMessage(subject, body, self.from_address,
                                      to_address)
        self.email.attach(self.attachment_name, self.attachment_content,
                          self.attachment_mime)
        self.email.send(fail_silently=False)
