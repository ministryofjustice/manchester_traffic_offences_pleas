# coding=utf-8

from datetime import datetime, timedelta
from mock import Mock

from django.core import mail
from django.forms.formsets import formset_factory
from django.test import TestCase
from django.utils import translation

from apps.forms.forms import RequiredFormSet

from ..email import send_plea_email
from ..models import Court
from ..forms import (NoticeTypeForm,
                     CaseForm,
                     YourDetailsForm,
                     PleaForm,
                     YourMoneyForm,
                     HardshipForm,
                     HouseholdExpensesForm,
                     OtherExpensesForm,
                     ConfirmationForm)


class EmailTemplateTests(TestCase):

    def setUp(self):
        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="test@test.com",
            submission_email="test@test.com",
            plp_email="test@test.com",
            enabled=True,
            test_mode=True)

    def get_context_data(self, notice_type_data=None, case_data=None, details_data=None, plea_data=None, finances_data=None, hardship_data=None, household_expenses_data=None, other_expenses_data=None, review_data=None):

        self.hearing_date = datetime.today() + timedelta(30)

        if not notice_type_data:
            notice_type_data = {"sjp": False}

        if not case_data:
            case_data = {"urn": "06/AA/00000/00",
                         "date_of_hearing_0": str(self.hearing_date.day),
                         "date_of_hearing_1": str(self.hearing_date.month),
                         "date_of_hearing_2": str(self.hearing_date.year),
                         "number_of_charges": 1,
                         "plea_made_by": "Defendant"}

        if not details_data:
            details_data = {"first_name": "Joe",
                            "last_name": "Public",
                            "correct_address": True,
                            "contact_number": "0161 123 2345",
                            "date_of_birth_0": "12",
                            "date_of_birth_1": "03",
                            "date_of_birth_2": "1980",
                            "have_ni_number": False,
                            "have_driving_licence_number": False}

        if not plea_data:
            plea_data = {"guilty": "guilty",
                         "guilty_extra": "IT wasn't me driving!"}

        if not finances_data:
            finances_data = {"you_are": "Employed",
                             "employed_take_home_pay_period": "Weekly",
                             "employed_take_home_pay_amount": "100",
                             "employed_hardship": False}

        if not hardship_data:
            hardship_data = {"hardship_details": "Lorem\nIpsum"}

        if not household_expenses_data:
            household_expenses_data = {"household_accommodation": 10,
                                       "household_utility_bills": 11,
                                       "household_insurance": 12,
                                       "household_council_tax": 13,
                                       "other_bill_payers": False}

        if not other_expenses_data:
            other_expenses_data = {"other_tv_subscription": 14,
                                   "other_travel_expenses": 15,
                                   "other_telephone": 16,
                                   "other_loan_repayments": 17,
                                   "other_court_payments": 18,
                                   "other_child_maintenance": 19}

        if not review_data:
            review_data = {"receive_email_updates": True,
                           "email": "test@test.com",
                           "understand": True}

        ntf = NoticeTypeForm(notice_type_data)
        cf = CaseForm(case_data)
        df = YourDetailsForm(details_data)
        pf = PleaForm(plea_data)
        mf = YourMoneyForm(finances_data)
        hf = HardshipForm(hardship_data)
        hef = HouseholdExpensesForm(household_expenses_data)
        oef = OtherExpensesForm(other_expenses_data)
        rf = ConfirmationForm(review_data)

        household_expense_fields = ["household_accommodation",
                                    "household_utility_bills",
                                    "household_insurance",
                                    "household_council_tax"]

        other_expense_fields = ["other_tv_subscription",
                                "other_travel_expenses",
                                "other_telephone",
                                "other_loan_repayments",
                                "other_court_payments",
                                "other_child_maintenance"]

        if all([ntf.is_valid(), cf.is_valid(), df.is_valid(), pf.is_valid(), mf.is_valid(), hf.is_valid(), hef.is_valid(), oef.is_valid(), rf.is_valid()]):
            data = {"notice_type": ntf.cleaned_data,
                    "case": cf.cleaned_data,
                    "your_details": df.cleaned_data,
                    "plea": {"data": [pf.cleaned_data]},
                    "your_finances": mf.cleaned_data,
                    "hardship": hf.cleaned_data,
                    "household_expenses": hef.cleaned_data,
                    "other_expenses": oef.cleaned_data,
                    "review": rf.cleaned_data}

            data["your_finances"]["hardship"] = any([
                mf.cleaned_data.get("employed_hardship", False),
                mf.cleaned_data.get("self_employed_hardship", False),
                mf.cleaned_data.get("receiving_benefits_hardship", False),
                mf.cleaned_data.get("other_hardship", False)])

            total_household = sum(int(hef.cleaned_data[field] or 0) for field in household_expense_fields)
            total_other = sum(int(oef.cleaned_data[field] or 0) for field in other_expense_fields)
            total_expenses = total_household + total_other

            data["your_expenses"] = {"total_household_expenses": total_household,
                                     "total_other_expenses": total_other,
                                     "total_expenses": total_expenses}

            return data
        else:
            raise Exception(ntf.errors, cf.errors, df.errors, pf.errors, mf.errors, hf.errors, hef.errors, oef.errors, rf.errors)

    def get_mock_response(self, html):
        response = Mock()
        response.status_code = 200
        response.content = html.encode("utf-8")
        response.__str__ = Mock()
        response.__str__.return_value = html.encode("utf-8")
        response.charset = "utf-8"
        response.streaming = False
        return response

    def test_subject_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[0].subject, "ONLINE PLEA: 06/AA/00000/00 DOH: {} PUBLIC Joe"
            .format(self.hearing_date.strftime("%Y-%m-%d")))

    def test_sjp_subject_output(self):
        context_data = self.get_context_data(notice_type_data={"sjp": True})

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[0].subject, "ONLINE PLEA: 06/AA/00000/00 <SJP> PUBLIC Joe")

    def test_notice_type_not_sjp_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<h1>Online plea</h1>", count=1, html=True)
        self.assertContains(response, "<th>Court hearing date</th>", count=1, html=True)

    def test_notice_type_sjp_output(self):
        context_data = self.get_context_data(notice_type_data={"sjp": True})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<h1>Online plea - SJP</h1>", count=1, html=True)
        self.assertContains(response, "<th>Posting date</th>", count=1, html=True)

    def test_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Unique reference number</th><td>06/AA/00000/00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Court hearing date</th><td>{}</td></tr>".format(self.hearing_date.strftime("%d/%m/%Y")), count=1, html=True)

    def test_case_details_output_is_english(self):
        translation.activate("cy")

        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        translation.deactivate()

        self.assertContains(response, "<tr><th>Unique reference number</th><td>06/AA/00000/00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Court hearing date</th><td>{}</td></tr>".format(self.hearing_date.strftime("%d/%m/%Y")), count=1, html=True)

    def test_welsh_journey_adds_welsh_flag(self):
        translation.activate("cy")

        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        translation.deactivate()

        self.assertContains(response, "<tr><th>Welsh language</th><td>Yes</td></tr>", count=1, html=True)

    def test_english_journey_adds_no_welsh_flag(self):
        translation.activate("en")

        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertNotContains(response, "<tr><th>Welsh language</th><td>Yes</td></tr>", html=True)

    def test_min_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>First name</th><td>Joe</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Last name</th><td>Public</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Address</th><td>As printed on the notice</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Contact number</th><td>0161 123 2345</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Date of birth</th><td>12/03/1980</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>National Insurance number</th><td>-</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>UK driving licence number</th><td>-</td></tr>", count=1, html=True)

    def test_full_case_details_output(self):
        context_data_details = {"first_name": "Joe",
                                "last_name": "Public",
                                "correct_address": False,
                                "updated_address": "Test address, Somewhere, TE57ER",
                                "contact_number": "0161 123 2345",
                                "date_of_birth_0": "12",
                                "date_of_birth_1": "03",
                                "date_of_birth_2": "1980",
                                "have_ni_number": True,
                                "ni_number": "QQ 12 34 56 Q",
                                "have_driving_licence_number": True,
                                "driving_licence_number": "TESTE12345"}

        context_data = self.get_context_data(details_data=context_data_details)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>First name</th><td>Joe</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Last name</th><td>Public</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Address</th><td>Test address, Somewhere, TE57ER</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Contact number</th><td>0161 123 2345</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Date of birth</th><td>12/03/1980</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>National Insurance number</th><td>QQ 12 34 56 Q</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>UK driving licence number</th><td>TESTE12345</td></tr>", count=1, html=True)

    def test_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Guilty</td></tr>", count=1, html=True)

    def test_multiple_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["data"].append({"guilty_extra": "test2", "guilty": "guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Guilty</td></tr>", count=2, html=True)

    def test_single_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"
        context_data["plea"]["data"][0]["not_guilty_extra"] = "dsa"
        context_data["plea"]["data"][0]["interpreter_needed"] = True
        context_data["plea"]["data"][0]["interpreter_language"] = "French"
        context_data["plea"]["data"][0]["disagree_with_evidence"] = True
        context_data["plea"]["data"][0]["disagree_with_evidence_details"] = "Disagreement"
        context_data["plea"]["data"][0]["witness_needed"] = True
        context_data["plea"]["data"][0]["witness_details"] = "Witness details"
        context_data["plea"]["data"][0]["witness_interpreter_needed"] = True
        context_data["plea"]["data"][0]["witness_interpreter_language"] = "German"

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your plea</th><td>Not guilty</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Not guilty because</th><td>dsa</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Interpreter required</th><td>Yes</td></tr>", count=2, html=True)
        self.assertContains(response, "<tr><th>Language</th><td>French</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Disagree with any evidence from a witness statement?</th><td>Yes</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Name of the witness and what you disagree with</th><td>Disagreement</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Wants to call a witness?</th><td>Yes</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Name, date of birth and address of the witness</th><td>Witness details</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Language</th><td>German</td></tr>", count=1, html=True)

    def test_multiple_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Not guilty</td></tr>", count=2, html=True)

    def test_mixed_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Guilty</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Your plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_employed_email_finances_output(self):
        context_data_finances = {"you_are": "Employed",
                                 "employed_take_home_pay_period": "Weekly",
                                 "employed_take_home_pay_amount": "200",
                                 "employed_hardship": False}
        context_data = self.get_context_data(finances_data=context_data_finances)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£200.00</td></tr>", count=1, html=True)

    def test_self_employed_email_finances_output(self):
        context_data_finances = {"you_are": "Self-employed",
                              "self_employed_pay_period": "Weekly",
                              "self_employed_pay_amount": "200",
                              "self_employed_hardship": False}
        context_data = self.get_context_data(finances_data=context_data_finances)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£200.00</td></tr>", count=1, html=True)

    def test_self_employed_other_email_finances_output(self):
        context_data_finances = {"you_are": "Self-employed",
                              "self_employed_pay_period": "Self-employed other",
                              "self_employed_pay_amount": "20",
                              "self_employed_pay_other": "by the window",
                              "self_employed_hardship": False}
        context_data = self.get_context_data(finances_data=context_data_finances)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>You get paid</th><td>Other</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Details</th><td>by the window</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£20.00</td></tr>", count=1, html=True)

    def test_benefits_email_finances_output(self):
        context_data_finances = {"you_are": "Receiving benefits",
                              "benefits_details": "Housing benefit\nUniversal Credit",
                              "benefits_dependents": True,
                              "benefits_period": "Weekly",
                              "benefits_amount": "120",
                              "receiving_benefits_hardship": False}
        context_data = self.get_context_data(finances_data=context_data_finances)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your benefits</th><td>Housing benefit<br/>Universal Credit</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Weekly</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120.00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Includes payment for dependents?</th><td>Yes</td></tr>", count=1, html=True)


    def test_benefits_other_email_finances_output(self):
        context_data_finances = {"you_are": "Receiving benefits",
                              "benefits_details": "Housing benefit\nUniversal Credit",
                              "benefits_dependents": True,
                              "benefits_period": "Benefits other",
                              "benefits_pay_other": "Other details!",
                              "benefits_amount": "120",
                              "receiving_benefits_hardship": False}
        context_data = self.get_context_data(finances_data=context_data_finances)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Your benefits</th><td>Housing benefit<br/>Universal Credit</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>You get paid</th><td>Other</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Details</th><td>Other details!</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120.00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Includes payment for dependents?</th><td>Yes</td></tr>", count=1, html=True)


    def test_other_email_finances_output(self):
        context_data_finances = {"you_are": "Other",
                              "other_details": u"I am a pensioner and I earn\n£500 a month.",
                              "other_pay_amount": "120",
                              "other_hardship": False}
        context_data = self.get_context_data(finances_data=context_data_finances)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Details</th><td>I am a pensioner and I earn<br />£500 a month.</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Amount</th><td>£120.00</td></tr>", count=1, html=True)


    def test_expenses_output_default(self):
        context_data_finances = {"you_are": "Employed",
                                 "employed_take_home_pay_period": "Weekly",
                                 "employed_take_home_pay_amount": "100",
                                 "employed_hardship": True}

        context_data = self.get_context_data(finances_data=context_data_finances)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Financial hardship details</th><td>Lorem<br />Ipsum</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Other contributors to household bills</th><td>No</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Total household expenses</th><td>£46.00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Total other expenses</th><td>£99.00</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Total expenses</th><td>£145.00</td></tr>", count=1, html=True)

    def test_expenses_output_other_contributors_yes(self):
        context_data_finances = {"you_are": "Employed",
                                 "employed_take_home_pay_period": "Weekly",
                                 "employed_take_home_pay_amount": "100",
                                 "employed_hardship": True}

        household_expenses_data = {"household_accommodation": 10,
                                   "household_utility_bills": 11,
                                   "household_insurance": 12,
                                   "household_council_tax": 13,
                                   "other_bill_payers": True}
        other_expenses_data = {"other_tv_subscription": 14,
                               "other_travel_expenses": 15,
                               "other_telephone": 16,
                               "other_loan_repayments": 17,
                               "other_court_payments": 18,
                               "other_child_maintenance": 19}

        context_data = self.get_context_data(finances_data=context_data_finances, household_expenses_data=household_expenses_data, other_expenses_data=other_expenses_data)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Other contributors to household bills</th><td>Yes</td></tr>", count=1, html=True)


    def test_skipped_email_finances_output(self):
        context_data = self.get_context_data()
        context_data["your_finances"] = {"skipped": True}

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContains(response, "<tr><th>Status</th><td><i>Not completed/provided Financial details must be collected at hearing</i></td></tr>", count=1, html=True)


    def test_receive_email_updates_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Email updates</th><td>Yes</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Email address</th><td>test@test.com</td></tr>", count=1, html=True)

    def test_receive_email_no_updates_output(self):
        context_data = self.get_context_data(review_data={"receive_email_updates": False, "understand": True})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<tr><th>Email updates</th><td>No</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Email address</th><td>-</td></tr>", count=1, html=True)


    # PLP Emails
    def test_PLP_subject_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[1].subject, "POLICE ONLINE PLEA: 06/AA/00000/00 DOH: {} PUBLIC Joe"
                         .format(self.hearing_date.strftime("%Y-%m-%d")))

    def test_PLP_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>First name</th><td>Joe</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Last name</th><td>Public</td></tr>", count=1, html=True)

    def test_PLP_case_details_output_is_english(self):
        translation.activate("cy")

        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])

        translation.deactivate()

        self.assertContains(response, "<tr><th>First name</th><td>Joe</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Last name</th><td>Public</td></tr>", count=1, html=True)

    def test_PLP_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Guilty</td></tr>", count=1, html=True)

    def test_PLP_multiple_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["data"].append({"guilty_extra": "test2", "guilty": "guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Guilty</td></tr>", count=2, html=True)

    def test_PLP_single_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_PLP_multiple_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Not guilty</td></tr>", count=2, html=True)

    def test_PLP_mixed_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContains(response, "<tr><th>Your plea</th><td>Guilty</td></tr>", count=1, html=True)
        self.assertContains(response, "<tr><th>Your plea</th><td>Not guilty</td></tr>", count=1, html=True)

    def test_plea_email_guilty_pleas(self):
        context_data = self.get_context_data()
        context_data["case"]["number_of_pleas"] = 3
        context_data["plea"]["data"] = [
            {
                "guilty": "guilty",
                "guilty_extra": "asdf"
            },
            {
                "guilty": "guilty",
                "guilty_extra": "asdf"
            },
            {
                "guilty": "guilty",
                "guilty_extra": "asdf"
            }
        ]

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[2].body)

        self.assertContains(response, "<<GUILTY>>")

    def test_plea_email_not_guilty_pleas(self):
        context_data = self.get_context_data()
        context_data["case"]["number_of_pleas"] = 3
        context_data["plea"]["data"] = [
            {
                "guilty": "not_guilty",
                "not_guilty_extra": "asdf"
            },
            {
                "guilty": "not_guilty",
                "not_guilty_extra": "asdf"
            },
            {
                "guilty": "not_guilty",
                "not_guilty_extra": "asdf"
            }
        ]

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[2].body)

        self.assertContains(response, "<<NOTGUILTY>>")

    def test_plea_email_mixed_pleas(self):
        context_data = self.get_context_data()
        context_data["case"]["number_of_pleas"] = 3
        context_data["plea"]["data"] = [
            {
                "guilty": "not_guilty",
                "not_guilty_extra": "asdf"
            },
            {
                "guilty": "guilty",
                "guilty_extra": "asdf"
            },
            {
                "guilty": "guilty",
                "guilty_extra": "asdf"
            }
        ]

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[2].body)

        self.assertContains(response, "<<MIXED>>")

    def test_plea_email_no_hardship(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertNotContains(response, "<<SHOWEXPENSES>>")

    def test_plea_email_with_hardship(self):
        context_data = self.get_context_data()

        context_data["your_finances"]["hardship"] = True
        context_data["your_expenses"] = {}
        context_data["your_expenses"]["other_bill_pays"] = True
        context_data["your_expenses"]["complete"] = True
        context_data["your_expenses"]["total_household_expenses"] = "101"
        context_data["your_expenses"]["total_other_expenses"] = "202"
        context_data["your_expenses"]["total_expenses"] = "303"

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "101")
        self.assertContains(response, "202")
        self.assertContains(response, "303")


class TestCompanyFinancesEmailLogic(TestCase):

    def setUp(self):

        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="test@test.com",
            submission_email="test@test.com",
            plp_email="test@test.com",
            enabled="test@test.com",
            test_mode="test@test.com")

        self.test_session_data = {
            "notice_type": {
                "complete": True,
                "sjp": False
            },
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Company representative"
            },
            "your_details": {
                "complete": True,
                "skipped": True
            },
            "company_details": {
                "company_name": "some company plc",
                "updated_address": "some place plc",
                "first_name": "John",
                "last_name": "Smith",
                "position_in_company": "a director",
                "contact_number": "0800 SOMECOMPANY"
            },
            "plea": {
                "complete": True,
                "data": [
                    {
                        "guilty": "not_guilty",
                        "not_guilty_extra": "something"
                    }
                ]
            },
            "your_finances": {
                "complete": True,
                "skipped": True
            },
            "company_finances": {
                "complete": True,
                "skipped": True
            },
            "your_expenses": {
                "complete": True,
                "skipped": True
            },
            "review": {
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

        self.test_session_data["plea"]["data"][0]["guilty"] = "guilty"
        del self.test_session_data["company_finances"]["skipped"]

        send_plea_email(self.test_session_data)

        attachment = mail.outbox[0].attachments[0][1]

        self.assertTrue("<<SHOWCOMPANYDETAILS>>" in attachment)
        self.assertTrue("<<SHOWYOURDETAILS>>" not in attachment)
        self.assertTrue("<<SHOWCOMPANYFINANCES>>" in attachment)
        self.assertTrue("<<SHOWEXPENSES>>" not in attachment)

