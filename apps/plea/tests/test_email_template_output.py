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
                "your_details": {"name": "Joe Public", "contact_number": "0161 123 2345",
                                 "email": "test@example.org", "national_insurance_number": "AB001122C",
                                 "driving_licence_number": "PUB54378493", "registration_number": "JO00 EPU"},
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

    def test_subject_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 PUBLIC Joe')

    def test_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>URN</th><td>00/AA/00000/00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Court hearing</th><td>30 October 2015 at 09:15</td></tr>", count=1, html=True)

    def test_min_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Full name</th><td>Joe Public</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Contact number</th><td>0161 123 2345</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Email</th><td>test@example.org</td></tr>", count=1, html=True)

    def test_full_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Full name</th><td>Joe Public</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Contact number</th><td>0161 123 2345</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Email</th><td>test@example.org</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>National Insurance number</th><td>AB001122C</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>UK driving licence number</th><td>PUB54378493</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Registration number</th><td>JO00 EPU</td></tr>", count=1, html=True)

    def test_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=1, html=True)

    def test_multiple_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=2, html=True)

    def test_single_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_multiple_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=2, html=True)

    def test_mixed_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

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

        send_plea_email(context_data)

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

        send_plea_email(context_data)

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

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your Job</th><td>Window cleaner</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Other - by the window</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£20</td></tr>", count=1, html=True)

    def test_benefits_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"you_are": "Receiving benefits",
                                      "benefits_period": "Weekly",
                                      "benefits_amount": "120"}

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120</td></tr>", count=1, html=True)

    def test_other_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"you_are": "Other",
                                      "other_info": "I am a pensioner and I earn\n£500 a month.",
                                      "benefits_amount": "120"}

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>More information</th><td>I am a pensioner and I earn<br />£500 a month.</td></tr>", count=1, html=True)

    def test_skipped_email_money_output(self):
        context_data = self.get_context_data()
        context_data["your_money"] = {"skipped": "True"}

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Status</th><td><i>Not completed/provided Financial details must be collected at hearing</i></td></tr>", count=1, html=True)

    # PLP Emails
    def test_PLP_subject_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[1].subject, 'POLICE ONLINE PLEA: 00/AA/00000/00 DOH: 2015-10-30 PUBLIC Joe')

    def test_PLP_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>URN</th><td>00/AA/00000/00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Court hearing</th><td>30 October 2015 at 09:15</td></tr>", count=1, html=True)

    def test_PLP_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Full name</th><td>Joe Public</td></tr>", count=1, html=True)

    def test_PLP_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=1, html=True)

    def test_PLP_multiple_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=2, html=True)

    def test_PLP_single_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_PLP_multiple_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"][0]["guilty"] = "not_guilty"
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=2, html=True)

    def test_PLP_mixed_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["PleaForms"].append({"mitigations": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Plea</th><td>Guilty</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_plea_email_guilty_pleas(self):
        context_data = self.get_context_data()
        context_data["case"]['number_of_pleas'] = 3
        context_data["plea"]["PleaForms"] = [
            {
                'guilty': 'guilty',
                'mitigations': 'asdf'
            },
            {
                'guilty': 'guilty',
                'mitigations': 'asdf'
            },
            {
                'guilty': 'guilty',
                'mitigations': 'asdf'
            }
        ]

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[2].body)

        self.assertContains(response, '<<GUILTY>>')

    def test_plea_email_not_guilty_pleas(self):
        context_data = self.get_context_data()
        context_data["case"]['number_of_pleas'] = 3
        context_data["plea"]["PleaForms"] = [
            {
                'guilty': 'not_guilty',
                'mitigations': 'asdf'
            },
            {
                'guilty': 'not_guilty',
                'mitigations': 'asdf'
            },
            {
                'guilty': 'not_guilty',
                'mitigations': 'asdf'
            }
        ]

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[2].body)

        self.assertContains(response, '<<NOTGUILTY>>')

    def test_plea_email_mixed_pleas(self):
        context_data = self.get_context_data()
        context_data["case"]['number_of_pleas'] = 3
        context_data["plea"]["PleaForms"] = [
            {
                'guilty': 'not_guilty',
                'mitigations': 'asdf'
            },
            {
                'guilty': 'guilty',
                'mitigations': 'asdf'
            },
            {
                'guilty': 'guilty',
                'mitigations': 'asdf'
            }
        ]

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[2].body)

        self.assertContains(response, '<<MIXED>>')