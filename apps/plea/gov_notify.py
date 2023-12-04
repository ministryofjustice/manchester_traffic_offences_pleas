from notifications_python_client.notifications import NotificationsAPIClient, prepare_upload
from make_a_plea.settings.dev import GOV_NOTIFY_API
from django.template.loader import render_to_string
import pdfkit


class GovNotify:

    def __init__(self, email_address, subject, personalisation, template_id):
        self.api_key: str = GOV_NOTIFY_API
        self.client: NotificationsAPIClient = NotificationsAPIClient(self.api_key)
        self.subject: str = subject
        self.email_address: str = email_address
        self.personalisation = personalisation
        self.template_id: str = template_id

    def send_email(self):
        return self.client.send_email_notification(
            self.email_address,
            self.personalisation,
            self.template_id
        )

    def upload_file_link(self, data, html_template):
        string_data = render_to_string(html_template, data)
        try:
            pdf_file = pdfkit.from_string(string_data, "plea_file.pdf", verbose=True)
            with open(pdf_file, 'rb') as file_:
                self.personalisation['link_to_file'] = prepare_upload(file_)
        except Exception as e:
            print(f'Error uploading file (plea_file.pdf) to notify with message: {e}')

