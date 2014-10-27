# coding=utf-8

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
                "your_money": {}}

    def get_mock_response(self, html):
        response = Mock()
        response.status_code = 200
        response.content = html.encode("utf-8")
        response.__str__ = Mock()
        response.__str__.return_value = html.encode("utf-8")
        response._charset = "utf-8"
        response.streaming = False
        return response

    def test_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=1, html=True)

    def test_multiple_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "guilty"})

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=2, html=True)

    def test_single_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_multiple_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=2, html=True)

    def test_mixed_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_employed_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"you_are": "Employed",
                                      "employer_name": "Tesco",
                                      "employer_address": "A big office\nSomewhere central\nAB12 123",
                                      "employer_phone": "012374384",
                                      "take_home_pay_period": "Weekly",
                                      "take_home_pay_amount": "200",
                                      }

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Employer's name</th><td>Tesco</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Employer's full address</th><td>A big office<br />Somewhere central<br />AB12 123</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Employer's phone</th><td>012374384</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£200</td></tr>", count=1, html=True)

    def test_self_employed_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"you_are": "Self employed",
                                      "your_job": "Tesco",
                                      "self_employed_pay_period": "Weekly",
                                      "self_employed_pay_amount": "200",
                                      }

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your Job</th><td>Tesco</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£200</td></tr>", count=1, html=True)

    def test_self_employed_other_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"you_are": "Self employed",
                                      "your_job": "Window cleaner",
                                      "self_employed_pay_period": "self-employed other",
                                      "self_employed_pay_amount": "20",
                                      "self_employed_pay_other": "by the window"
                                      }

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your Job</th><td>Window cleaner</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Other - by the window</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£20</td></tr>", count=1, html=True)

    def test_benefits_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"you_are": "Receiving benefits",
                                      "benefits_period": "Weekly",
                                      "benefits_amount": "120"}

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120</td></tr>", count=1, html=True)

    def test_other_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"you_are": "Other",
                                      "other_info": "I am a pensioner and I earn\n£500 a month.",
                                      "benefits_amount": "120"}

        with self.settings(SEND_PLEA_CONFIRMATION_EMAIL=False):
            send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 GEORGE Ian')
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>More information</th><td>I am a pensioner and I earn<br />£500 a month.</td></tr>", count=1, html=True)
