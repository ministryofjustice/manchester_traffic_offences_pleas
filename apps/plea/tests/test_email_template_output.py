from django.test import TestCase
from django.core import mail
from mock import Mock

from ..email import TemplateAttachmentEmail, send_plea_email
from ..models import CourtEmailPlea, CourtEmailCount


class EmailTemplateTests(TestCase):
    def get_context_data(self):
        return {"case": {"date_of_hearing": "2015-10-30",
                         "time_of_hearing": "09:15:00",
                         "urn": "00/AA/00000/00",
                         "number_of_charges": 1},
                "your_details": {"name": "Ian George", "national_insurance_number": "xxx",
                                 "driving_licence_number": "xxx", "registration_number": "xxx"},
                "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"}],
                         "understand": True},
                "your_money": {

                }}

    def get_fake_response(self, html):
        response = Mock()
        response.status_code = 200
        response.content = html
        response.__str__ = Mock()
        response.__str__.return_value = html
        response._charset = "UTF-8"
        response.streaming = False
        return response

    def test_single_guilty_plea_email_output(self):
        context_data = self.get_context_data()
        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].body, "<<<makeaplea-ref: 12/7>>>")

        response = self.get_fake_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=1, html=True)

    def test_multiple_guilty_plea_email_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "guilty"})

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].body, "<<<makeaplea-ref: 10/5>>>")

        response = self.get_fake_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=2, html=True)

    def test_single_not_guilty_plea_email_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].body, "<<<makeaplea-ref: 13/8>>>")

        response = self.get_fake_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_multiple_not_guilty_plea_email_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].body, "<<<makeaplea-ref: 11/6>>>")

        response = self.get_fake_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=2, html=True)

    def test_mixed_plea_email_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].body, "<<<makeaplea-ref: 9/4>>>")

        response = self.get_fake_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=1, html=True)