# coding=utf-8

from datetime import datetime, timedelta
from mock import Mock

from django.core import mail
from django.forms.formsets import formset_factory
from django.test import TestCase

from ..email import send_plea_email
from ..models import Court
from ..forms import CaseForm, YourDetailsForm, PleaForm, YourMoneyForm, RequiredFormSet


class EmailTemplateTests(TestCase):
    def setUp(self):
        Court.objects.create(
            region_code="06",
            court_name="x",
            court_address="x",
            court_telephone="x",
            court_email="x",
            submission_email="test@test.com",
            plp_email="plptest@test.com",
            enabled=True,
            test_mode=False)

    def get_context_data(self, case_data=None, details_data=None, plea_data=None, money_data=None):

        self.hearing_date = datetime.today() + timedelta(30)

        if not case_data:
            case_data = {"urn_0": "06",
                         "urn_1": "AA",
                         "urn_2": "00000",
                         "urn_3": "00",
                         "date_of_hearing_0": str(self.hearing_date.day),
                         "date_of_hearing_1": str(self.hearing_date.month),
                         "date_of_hearing_2": str(self.hearing_date.year),
                         "number_of_charges": 1,
                         "company_plea": False}

        if not details_data:
            details_data = {"name": "Joe Public",
                            "contact_number": "0161 123 2345",
                            "email": "test@example.org"}

        if not plea_data:
            plea_data = {"form-TOTAL_FORMS": "1",
                         "form-INITIAL_FORMS": "1",
                         "form-MAX_NUM_FORMS": "1",
                         "form-0-guilty": "guilty",
                         "form-0-mitigations": "IT wasn't me driving!"}

        if not money_data:
            money_data = {"you_are": "Employed",
                          "employed_your_job": "Some Job",
                          "employed_take_home_pay_period": "Weekly",
                          "employed_take_home_pay_amount": "100",
                          "employed_hardship": False}

        PleaForms = formset_factory(PleaForm, formset=RequiredFormSet, extra=1, max_num=1)

        cf = CaseForm(case_data)
        df = YourDetailsForm(details_data)
        pf = PleaForms(plea_data)
        mf = YourMoneyForm(money_data)

        if all([cf.is_valid(), df.is_valid(), pf.is_valid(), mf.is_valid()]):
            data = {"case": cf.cleaned_data,
                    "your_details": df.cleaned_data,
                    "plea": {"PleaForms": pf.cleaned_data},
                    "your_money": mf.cleaned_data}
            return data
        else:
            raise Exception(cf.errors, df.errors, pf.errors, mf.errors)

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
        self.assertEqual(mail.outbox[0].subject, 'ONLINE PLEA: 06/AA/00000/00 DOH: {} PUBLIC Joe'
            .format(self.hearing_date.strftime('%Y-%m-%d')))

    def test_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>URN</th><td>06/AA/00000/00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Court hearing</th><td>{}</td></tr>".format(self.hearing_date.strftime('%d %B %Y')), count=1, html=True)

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
        context_data_money = {"you_are": "Employed",
                              "employed_your_job": "Some Job",
                              "employed_take_home_pay_period": "Weekly",
                              "employed_take_home_pay_amount": "200",
                              "employed_hardship": False}
        context_data = self.get_context_data(money_data=context_data_money)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your Job</th><td>Some Job</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Take home pay</th><td>£200</td></tr>", count=1, html=True)

    def test_self_employed_email_money_output(self):
        context_data_money = {"you_are": "Self-employed",
                              "your_job": "Tesco",
                              "self_employed_pay_period": "Weekly",
                              "self_employed_pay_amount": "200",
                              "self_employed_hardship": False}
        context_data = self.get_context_data(money_data=context_data_money)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your Job</th><td>Tesco</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£200</td></tr>", count=1, html=True)

    def test_self_employed_other_email_money_output(self):
        context_data_money = {"you_are": "Self-employed",
                              "your_job": "Window cleaner",
                              "self_employed_pay_period": "Self-employed other",
                              "self_employed_pay_amount": "20",
                              "self_employed_pay_other": "by the window",
                              "self_employed_hardship": False}
        context_data = self.get_context_data(money_data=context_data_money)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your Job</th><td>Window cleaner</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Other - by the window</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£20</td></tr>", count=1, html=True)

    def test_benefits_email_money_output(self):
        context_data_money = {"you_are": "Receiving benefits",
                              "benefits_details": "Housing benefit\nUniversal Credit",
                              "benefits_dependents": "Yes",
                              "benefits_period": "Weekly",
                              "benefits_amount": "120",
                              "receiving_benefits_hardship": False}
        context_data = self.get_context_data(money_data=context_data_money)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Benefits you receive</th><td>Housing benefit\nUniversal Credit</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Does this include payment for dependents?</th><td>Yes</td></tr>", count=1, html=True)


    def test_benefits_other_email_money_output(self):
        context_data_money = {"you_are": "Receiving benefits",
                              "benefits_details": "Housing benefit\nUniversal Credit",
                              "benefits_dependents": "Yes",
                              "benefits_period": "Benefits other",
                              "benefits_pay_other": "Other details!",
                              "benefits_amount": "120",
                              "receiving_benefits_hardship": False}
        context_data = self.get_context_data(money_data=context_data_money)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Benefits you receive</th><td>Housing benefit\nUniversal Credit</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Other - Other details!</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Does this include payment for dependents?</th><td>Yes</td></tr>", count=1, html=True)


    def test_other_email_money_output(self):
        context_data_money = {"you_are": "Other",
                              "other_details": u"I am a pensioner and I earn\n£500 a month.",
                              "other_pay_amount": "120",
                              "other_hardship": False}
        context_data = self.get_context_data(money_data=context_data_money)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>More information</th><td>I am a pensioner and I earn<br />£500 a month.</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120</td></tr>", count=1, html=True)

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
        self.assertEqual(mail.outbox[1].subject, 'POLICE ONLINE PLEA: 06/AA/00000/00 DOH: {} PUBLIC Joe'
                         .format(self.hearing_date.strftime('%Y-%m-%d')))

    def test_PLP_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>URN</th><td>06/AA/00000/00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Court hearing</th><td>30 October 2015</td></tr>", count=1, html=True)

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

    def test_plea_email_no_hardship(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertNotContains(response, '<<SHOWEXPENSES>>')

    def test_plea_email_with_hardship(self):
        context_data = self.get_context_data()

        context_data['your_money']['hardship'] = True
        context_data['your_expenses'] = {}
        context_data['your_expenses']['other_bill_pays'] = True
        context_data['your_expenses']['complete'] = True
        context_data['your_expenses']['total_household_expenses'] = "101"
        context_data['your_expenses']['total_other_expenses'] = "202"
        context_data['your_expenses']['total_expenses'] = "303"

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '101')
        self.assertContains(response, '202')
        self.assertContains(response, '303')


class TestCompanyFinancesEmailLogic(TestCase):

    def setUp(self):

        Court.objects.create(
            region_code="06",
            court_name="x",
            court_address="x",
            court_telephone="x",
            court_email="x",
            submission_email="test@test.com",
            plp_email="plptest@test.com",
            enabled=True,
            test_mode=False)

        self.test_session_data = {
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "company_plea": True
            },
            'your_details': {
                "complete": True,
                "skipped": True
            },
            "company_details": {
                "company_name": "some company plc",
                "company_address": "some place plc",
                "name": "mr smith",
                "position_in_company": "a director",
                "contact_number": "0800 SOMECOMPANY",
                "email": "test@companyemail.com"
            },
            "plea": {
                "complete": True,
                "PleaForms": [
                    {
                        "guilty": "not_guilty",
                        "mitigations": "something"
                    }
                ]
            },
            'your_money': {
                "complete": True,
                "skipped": True
            },
            "company_finances": {
                "complete": True,
                "skipped": True
            },
            'your_expenses': {
                "complete": True,
                "skipped": True
            },
            'review': {
                "complete": True
            }
        }

    def test_company_details_without_company_finances(self):
        """
        If the user's pleas are all not guilty, there shouldn't be a company
        finance block
        """

        send_plea_email(self.test_session_data)

        attachment = mail.outbox[0].attachments[0][1]

        self.assertTrue("<<SHOWCOMPANYDETAILS>>" in attachment)
        self.assertTrue("<<SHOWYOURDETAILS>>" not in attachment)
        self.assertTrue("<<SHOWCOMPANYFINANCES>>" not in attachment)
        self.assertTrue("<<SHOWEXPENSES>>" not in attachment)

    def test_company_details_with_company_finances(self):

        self.test_session_data["plea"]["PleaForms"][0]["guilty"] = "guilty"
        del self.test_session_data["company_finances"]["skipped"]

        send_plea_email(self.test_session_data)

        attachment = mail.outbox[0].attachments[0][1]

        self.assertTrue("<<SHOWCOMPANYDETAILS>>" in attachment)
        self.assertTrue("<<SHOWYOURDETAILS>>" not in attachment)
        self.assertTrue("<<SHOWCOMPANYFINANCES>>" in attachment)
        self.assertTrue("<<SHOWEXPENSES>>" not in attachment)

