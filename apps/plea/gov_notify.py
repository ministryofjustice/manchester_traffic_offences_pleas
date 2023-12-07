from django.template.loader import render_to_string
from notifications_python_client import prepare_upload
from notifications_python_client.notifications import NotificationsAPIClient
from xhtml2pdf import pisa
from io import BytesIO

from make_a_plea.settings.dev import GOV_NOTIFY_API


class GovNotify:

    def __init__(self, email_address, personalisation, template_id):
        self.api_key: str = GOV_NOTIFY_API
        self.client: NotificationsAPIClient = NotificationsAPIClient(self.api_key)
        self.email_address: str = email_address
        self.personalisation = personalisation
        self.template_id: str = template_id

    def send_email(self):
        self.client.send_email_notification(
            email_address=self.email_address,
            personalisation=self.personalisation,
            template_id=self.template_id
        )

    # @staticmethod
    # def create_pdf_from_html(html: str):
    #     pdf_stream: BytesIO = BytesIO()
    #     pisa.CreatePDF(html, dest=pdf_stream)
    #     pdf_stream.seek(0)
    #     # return pdf_stream
    #     with open(html, 'w+b'):
    #         return pisa.CreatePDF(html, dest='plea_file.pdf')

    def upload_file_link(self, data, html_template):
        string_data = render_to_string(html_template, data)
        try:
            with open('plea_file.pdf', 'w+b') as file_:
                pisa.CreatePDF(string_data, dest=file_)
                self.personalisation['link_to_file'] = prepare_upload(file_)
        except Exception as e:
            print(f'Error uploading file (plea_file.pdf) to notify with message: {e}')
