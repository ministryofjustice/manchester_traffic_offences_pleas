from django.conf import settings
from django.core.mail import message, get_connection
from django.template.loader import render_to_string
from notifications_python_client import prepare_upload
from notifications_python_client.notifications import NotificationsAPIClient
from .pdf import PDFUtils


class GovNotifyClient(message.EmailMessage):

    def __init__(self, subject, body, to, template_id):
        super().__init__(subject=subject, body=body, to=to, connection=get_connection(backend=settings.EMAIL_BACKEND))
        self.client: NotificationsAPIClient = NotificationsAPIClient(settings.GOV_NOTIFY_API)
        self.email_address: str = to[0]
        self.personalisation = {'subject': subject, 'email_body': body, 'link_to_file': ''}
        self.template_id: str = template_id

    def send(self, fail_silently=False):
        super().send()
        return self.client.send_email_notification(
            email_address=self.email_address,
            personalisation=self.personalisation,
            template_id=self.template_id
        )

    def upload_file_link(self, data, html_template):
        try:
            string_data = render_to_string(html_template, data)
            pdf_file = PDFUtils.create_pdf_from_html(string_data)
            self.personalisation['link_to_file'] = prepare_upload(pdf_file)
        except Exception as e:
            print(f'Error uploading file to notify with message: {e}')
            self.personalisation['link_to_file'] = 'There was an issue attaching the pdf file'
