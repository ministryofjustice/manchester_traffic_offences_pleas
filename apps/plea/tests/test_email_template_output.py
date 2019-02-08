# coding=utf-8
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from mock import Mock, patch

from django.core import mail
from django.test import TestCase
from django.utils import translation
from ..email import send_plea_email
from ..models import Court, Case
from ..forms import (URNEntryForm,
                     NoticeTypeForm,
                     CaseForm,
                     YourDetailsForm,
                     PleaForm,
                     YourStatusForm,
                     YourIncomeForm,
                     HardshipForm,
                     HouseholdExpensesForm,
                     OtherExpensesForm,
                     ConfirmationForm)


class BaseEmailTemplateTests(TestCase):
    def assertContainsDefinition(self, content, label, value, count=None):
        pair_regex_tpl = r"<dt[^>]*>{0}</dt>\s*<dd[^>]*>{1}</dd>"
        pair_regex = pair_regex_tpl.format(re.escape(label), re.escape(value))
        matches = re.findall(pair_regex.encode(), content)
        if not matches:
            raise AssertionError("Definition pair \"" + label + "\"/\"" + value + "\" not found")

        if count is not None and len(matches) != count:
            error_tpl = 'Definition pair "{}"/"{}" found {} times (expected {})'
            raise AssertionError(error_tpl.format(label, value, len(matches), count))

    def setUp(self):
        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 12345678",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            test_mode=True)

    def get_context_data(self,
                         urn_entry_data=None,
                         notice_type_data=None,
                         case_data=None,
                         details_data=None,
                         plea_data=None,
                         status_data=None,
                         income_data=None,
                         hardship_data=None,
                         household_expenses_data=None,
                         other_expenses_data=None,
                         review_data=None):

        self.hearing_date = datetime.today() + timedelta(30)
        self.hearing_date_formatted = self.hearing_date.strftime("%d/%m/%Y")

        if not urn_entry_data:
            urn_entry_data = {"urn": "06AA0000000"}

        if not notice_type_data:
            notice_type_data = {"sjp": False}

        if not case_data:
            case_data = {"date_of_hearing_0": str(self.hearing_date.day),
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
                            "email": "user@example.org",
                            "have_ni_number": False,
                            "no_ni_number_reason": "Lost my NI card",
                            "have_driving_licence_number": False}

        if not plea_data:
            plea_data = {"guilty": "guilty_no_court",
                         "guilty_extra": "IT wasn't me driving!",
                         "hearing_language": True,
                         "documentation_language": True}

        if not status_data:
            status_data = {"you_are": "Employed"}

        if not income_data:
            income_data = {"sources": {"your_employment": {"label": "Employment",
                                                           "pay_period": "Weekly",
                                                           "pay_amount": 130}},
                           "weekly_total": 130,
                           "hardship": False}

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
                                   "other_child_maintenance": 19,
                                   "other_not_listed": True,
                                   "other_not_listed_details": "Lorem",
                                   "other_not_listed_amount": 10}

        if not review_data:
            review_data = {"understand": True}

        uf = URNEntryForm(urn_entry_data)
        ntf = NoticeTypeForm(notice_type_data)
        cf = CaseForm(case_data)
        df = YourDetailsForm(details_data)
        pf = PleaForm(plea_data)
        sf = YourStatusForm(status_data)
        yif = YourIncomeForm(income_data)
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
                                "other_child_maintenance",
                                "other_not_listed_amount"]

        all_forms = [uf, ntf, cf, df, pf, sf, yif, hf, hef, oef, rf]

        if not all([form.is_valid() for form in all_forms]):
            raise Exception(*[form.errors for form in all_forms])
        data = {"notice_type": ntf.cleaned_data,
                "case": cf.cleaned_data,
                "your_details": df.cleaned_data,
                "plea": {"data": [pf.cleaned_data]},
                "your_status": sf.cleaned_data,
                "your_income": income_data,
                "hardship": hf.cleaned_data,
                "household_expenses": hef.cleaned_data,
                "other_expenses": oef.cleaned_data,
                "review": rf.cleaned_data}

        data["case"].update(uf.cleaned_data)

        if "date_of_hearing" in data["case"]:
            data["case"]["contact_deadline"] = data["case"]["date_of_hearing"]

        if "posting_date" in data["case"]:
            data["case"]["contact_deadline"] = data["case"]["posting_date"] + relativedelta(days=+28)

        total_household = sum(int(hef.cleaned_data[field] or 0) for field in household_expense_fields)
        total_other = sum(int(oef.cleaned_data[field] or 0) for field in other_expense_fields)
        total_expenses = total_household + total_other

        data["your_expenses"] = {"total_household_expenses": total_household,
                                 "total_other_expenses": total_other,
                                 "total_expenses": total_expenses}

        return data

    def get_mock_response(self, html):
        response = Mock()
        response.status_code = 200
        response.content = html.encode("utf-8")
        response.__str__ = Mock()
        response.__str__.return_value = html.encode("utf-8")
        response.charset = "utf-8"
        response.streaming = False
        return response


class CourtEmailTemplateTests(BaseEmailTemplateTests):
    def test_subject_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(
            mail.outbox[0].subject,
            "ONLINE PLEA: 06/AA/0000000/00 DOH: {} PUBLIC Joe".format(self.hearing_date.strftime("%Y-%m-%d")))

    def test_subject_output_has_optional_middle_name(self):
        context_data = self.get_context_data()
        context_data['your_details']['middle_name'] = 'Bob'
        send_plea_email(context_data)

        self.assertEqual(
            mail.outbox[0].subject,
            "ONLINE PLEA: 06/AA/0000000/00 DOH: {} PUBLIC Joe Bob".format(self.hearing_date.strftime("%Y-%m-%d")))

    def test_sjp_subject_output(self):
        context_data = self.get_context_data(notice_type_data={"sjp": True})

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[0].subject, "ONLINE PLEA: 06/AA/0000000/00 <SJP> PUBLIC Joe")

    def test_notice_type_not_sjp_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<h1>Online plea</h1>", count=1, html=True)
        self.assertContains(response, "<dt>Court hearing date</dt>", count=1, html=True)

    def test_notice_type_sjp_output(self):
        context_data = self.get_context_data(notice_type_data={"sjp": True})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, "<h1>Online plea - SJP</h1>", count=1, html=True)
        self.assertContains(response, "<dt>Posting date</dt>", count=1, html=True)

    def test_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "Unique reference number", "06/AA/0000000/00", count=1)
        self.assertContainsDefinition(response.content, "Court hearing date", self.hearing_date_formatted, count=1)


    @patch("django.utils.translation.get_language", return_value='en')
    def test_english_journey_adds_no_welsh_flag(self, get_language):

        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertNotContains(response, "<dt>Welsh language</dt>", html=True)

    def test_min_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "First name", "Joe", count=1)
        self.assertContainsDefinition(response.content, "Last name", "Public", count=1)
        self.assertContainsDefinition(response.content, "Address", "As printed on the notice", count=1)
        self.assertContainsDefinition(response.content, "Contact number", "0161 123 2345", count=1)
        self.assertContainsDefinition(response.content, "Date of birth", "12/03/1980", count=1)
        self.assertContainsDefinition(response.content, "National Insurance number", "Lost my NI card", count=1)
        self.assertContainsDefinition(response.content, "UK driving licence number", "-", count=1)

    def test_full_case_details_output(self):
        context_data_details = {"first_name": "Joe",
                                "middle_name": "Bob",
                                "last_name": "Public",
                                "correct_address": False,
                                "updated_address": "Test address, Somewhere, TE57ER",
                                "contact_number": "0161 123 2345",
                                "date_of_birth_0": "12",
                                "date_of_birth_1": "03",
                                "date_of_birth_2": "1980",
                                "email": "user@example.org",
                                "have_ni_number": True,
                                "ni_number": "QQ 12 34 56 Q",
                                "have_driving_licence_number": True,
                                "driving_licence_number": "TESTE12345"}

        context_data = self.get_context_data(details_data=context_data_details)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "First name", "Joe", count=1)
        self.assertContainsDefinition(response.content, "Last name", "Public", count=1)
        self.assertContainsDefinition(response.content, "Middle name", "Bob", count=1)
        self.assertContainsDefinition(response.content, "Address", "Test address, Somewhere, TE57ER", count=1)
        self.assertContainsDefinition(response.content, "Contact number", "0161 123 2345", count=1)
        self.assertContainsDefinition(response.content, "Date of birth", "12/03/1980", count=1)
        self.assertContainsDefinition(response.content, "National Insurance number", "QQ 12 34 56 Q", count=1)
        self.assertContainsDefinition(response.content, "UK driving licence number", "TESTE12345", count=1)

    def test_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "Your plea", "Guilty", count=1)
        self.assertNotContains(response, "Hearing preference")
        self.assertNotContains(response, "Documentation preference")

    def test_SJP_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["notice_type"]["sjp"] = True
        context_data["plea"]["data"][0]["guilty"] = "guilty_court"
        context_data["plea"]["data"][0]["come_to_court"] = True
        context_data["plea"]["data"][0]["show_interpreter_question"] = True
        context_data["plea"]["data"][0]["sjp_interpreter_needed"] = True
        context_data["plea"]["data"][0]["sjp_interpreter_language"] = "French"
        context_data["plea"]["data"][0]["hearing_language"] = True
        context_data["plea"]["data"][0]["documentation_language"] = True


        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContainsDefinition(response.content, "Your plea", "Guilty", count=1)
        self.assertContainsDefinition(response.content, "Plead guilty in court", "Yes", count=1)
        self.assertContainsDefinition(response.content, "Interpreter required", "Yes", count=1)
        self.assertContainsDefinition(response.content, "Language", "French", count=1)
        self.assertNotContains(response, "Hearing preference")
        self.assertNotContains(response, "Documentation preference")

    def test_multiple_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["data"].append({"guilty_extra": "test2", "guilty": "guilty_no_court"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "Your plea", "Guilty", count=2)

    def test_single_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"
        context_data["plea"]["data"][0]["not_guilty_extra"] = "dsa"
        context_data["plea"]["data"][0]["show_interpreter_question"] = True
        context_data["plea"]["data"][0]["interpreter_needed"] = True
        context_data["plea"]["data"][0]["interpreter_language"] = "French"
        context_data["plea"]["data"][0]["disagree_with_evidence"] = True
        context_data["plea"]["data"][0]["disagree_with_evidence_details"] = "Disagreement"
        context_data["plea"]["data"][0]["witness_needed"] = True
        context_data["plea"]["data"][0]["witness_details"] = "Witness details"
        context_data["plea"]["data"][0]["witness_interpreter_needed"] = True
        context_data["plea"]["data"][0]["witness_interpreter_language"] = "German"
        context_data["plea"]["data"][0]["hearing_language"] = True
        context_data["plea"]["data"][0]["documentation_language"] = True

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "Your plea", "Not guilty", count=1)
        self.assertContainsDefinition(response.content, "Not guilty because", "dsa", count=1)
        # One for the defendant, one for the witness
        self.assertContainsDefinition(response.content, "Interpreter required", "Yes", count=2)
        self.assertContainsDefinition(response.content, "Language", "French", count=1)
        self.assertContainsDefinition(response.content,
                                      "Disagree with any evidence from a witness statement?", "Yes", count=1)
        self.assertContainsDefinition(response.content,
                                      "Name of the witness and what you disagree with", "Disagreement", count=1)
        self.assertContainsDefinition(response.content, "Wants to call a witness?", "Yes", count=1)
        self.assertContainsDefinition(response.content,
                                      "Name, date of birth and address of the witness", "Witness details", count=1)
        self.assertContainsDefinition(response.content, "Language", "German", count=1)
        self.assertNotContains(response, "Hearing preference")
        self.assertNotContains(response, "Documentation preference")

    def test_multiple_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"
        context_data["plea"]["data"][0]["hearing_language"] = True
        context_data["plea"]["data"][0]["documentation_language"] = True
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty",
                                             "hearing_language": True, "documentation_language": True})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "Your plea", "Not guilty", count=2)
        self.assertNotContains(response, "Hearing preference")
        self.assertNotContains(response, "Documentation preference")

    def test_mixed_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty",
                                             "hearing_language": True, "documentation_language": True})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "Your plea", "Guilty", count=1)
        self.assertContainsDefinition(response.content, "Your plea", "Not guilty", count=1)
        self.assertNotContains(response, "Hearing preference")
        self.assertNotContains(response, "Documentation preference")

    def test_status_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "You are", "Employed")

    def test_employed_weekly_output(self):
        context_data_income = {"sources": {"your_employment": {"label": "Employment",
                                                               "pay_period": "Weekly",
                                                               "pay_amount": 123}},
                               "weekly_total": 123,
                               "hardship": False}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '<h3>Your employment</h3>', html=True, count=1)
        self.assertContainsDefinition(response.content, "You get paid", "Weekly", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£123.00", count=2)

    def test_employed_fortnightly_output(self):
        context_data_income = {"sources": {"your_employment": {"label": "Employment",
                                                               "pay_period": "Fortnightly",
                                                               "pay_amount": 130}},
                               "weekly_total": 65,
                               "hardship": False}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '<h3>Your employment</h3>', html=True, count=1)
        self.assertContainsDefinition(response.content, "You get paid", "Fortnightly", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£130.00", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£65.00", count=1)

    def test_employed_monthly_output(self):
        context_data_income = {"sources": {"your_employment": {"label": "Employment",
                                                               "pay_period": "Monthly",
                                                               "pay_amount": 130}},
                               "weekly_total": 30,
                               "hardship": False}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '<h3>Your employment</h3>', html=True, count=1)
        self.assertContainsDefinition(response.content, "You get paid", "Monthly", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£130.00", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£30.00", count=1)

    def test_self_employed_weekly_output(self):
        context_data_income = {"sources": {"your_self_employment": {"label": "Self-employment",
                                                                    "pay_period": "Weekly",
                                                                    "pay_amount": 123}},
                               "weekly_total": 123,
                               "hardship": False}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '<h3>Your self-employment</h3>', html=True, count=1)
        self.assertContainsDefinition(response.content, "You get paid", "Weekly", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£123.00", count=2)

    def test_self_employed_fortnightly_output(self):
        context_data_income = {"sources": {"your_self_employment": {"label": "Self-employment",
                                                                    "pay_period": "Fortnightly",
                                                                    "pay_amount": 130}},
                               "weekly_total": 65,
                               "hardship": False}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '<h3>Your self-employment</h3>', html=True, count=1)
        self.assertContainsDefinition(response.content, "You get paid", "Fortnightly", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£130.00", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£65.00", count=1)

    def test_self_employed_monthly_output(self):
        context_data_income = {"sources": {"your_self_employment": {"label": "Self-employment",
                                                                    "pay_period": "Monthly",
                                                                    "pay_amount": 130}},
                               "weekly_total": 30,
                               "hardship": False}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '<h3>Your self-employment</h3>', html=True, count=1)
        self.assertContainsDefinition(response.content, "You get paid", "Monthly", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£130.00", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£30.00", count=1)

    def test_employed_with_benefits_weekly_output(self):
        context_data_income = {"sources": {"your_employment": {"label": "Employment",
                                                               "pay_period": "Weekly",
                                                               "pay_amount": 666},
                                           "your_benefits": {"label": "Benefits",
                                                             "pay_period": "Weekly",
                                                             "pay_amount": 111,
                                                             "benefit_type": "Income support"}},
                               "weekly_total": 777,
                               "hardship": False}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContains(response, '<h3>Your benefits</h3>', html=True, count=1)
        self.assertContainsDefinition(response.content, "You receive", "Income support", count=1)
        self.assertContainsDefinition(response.content, "Your benefits are paid", "Weekly", count=1)
        self.assertContainsDefinition(response.content, "Amount", "£111.00", count=1)

    def test_expenses_output_default(self):
        context_data_income = {"hardship": True}

        context_data = self.get_context_data(income_data=context_data_income)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(
            response.content,
            "Paying a fine would cause me financial problems because", "Lorem<br />Ipsum",
            count=1)
        self.assertContainsDefinition(response.content, "Other contributors to household bills", "No", count=1)
        self.assertContainsDefinition(response.content, "Total household expenses", "£46.00", count=1)
        self.assertContainsDefinition(response.content, "Total other expenses", "£109.00", count=1)
        self.assertContainsDefinition(response.content, "Total expenses", "£155.00", count=1)

    def test_expenses_output_other_contributors_yes(self):
        context_data_income = {"hardship": True}

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
                               "other_child_maintenance": 19,
                               "other_not_listed": False}

        context_data = self.get_context_data(
            income_data=context_data_income,
            household_expenses_data=household_expenses_data,
            other_expenses_data=other_expenses_data)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContainsDefinition(response.content, "Other contributors to household bills", "Yes", count=1)

    def test_expenses_output_not_listed(self):
        context_data_income = {"hardship": True}

        household_expenses_data = {"household_accommodation": 10,
                                   "household_utility_bills": 11,
                                   "household_insurance": 12,
                                   "household_council_tax": 13,
                                   "other_bill_payers": False}
        other_expenses_data = {"other_tv_subscription": 14,
                               "other_travel_expenses": 15,
                               "other_telephone": 16,
                               "other_loan_repayments": 17,
                               "other_court_payments": 18,
                               "other_child_maintenance": 19,
                               "other_not_listed": True,
                               "other_not_listed_details": "Extra expenses.",
                               "other_not_listed_amount": 10}

        context_data = self.get_context_data(
            income_data=context_data_income,
            household_expenses_data=household_expenses_data,
            other_expenses_data=other_expenses_data)

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContainsDefinition(response.content, "Other expenses (not listed)", "Extra expenses.", count=1)

    def test_skipped_email_finances_output(self):
        context_data = self.get_context_data()
        context_data["your_income"] = {"complete": True, "skipped": True}

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])
        self.assertContainsDefinition(
            response.content,
            "Status", "<i>Not completed/provided Financial details must be collected at hearing</i>",
            count=1)

    def test_receive_email_updates_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, "Email address", "user@example.org", count=1)

    def test_receive_company_email_updates_output(self):
        context_data = self.get_context_data()
        context_data['case']['plea_made_by'] = 'Company representative'
        context_data['your_details'] = {'complete': True, 'skipped': True}
        context_data['company_details'] = {
            'company_name': 'example company',
            'correct_address': True,
            'first_name': 'Example',
            'last_name': 'Example',
            'position_in_company': 'a director',
            'contact_number': '00000000',
            'email': 'company@example.org',
        }

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertContainsDefinition(response.content, 'Work email address', 'company@example.org', count=1)

    def test_plea_email_no_hardship(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[0].attachments[0][1])

        self.assertNotContains(response, "<<SHOWEXPENSES>>")

    def test_plea_email_with_hardship(self):
        context_data = self.get_context_data()

        context_data["your_income"]["hardship"] = True
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


class PLPEmailTemplateTests(BaseEmailTemplateTests):
    def test_PLP_subject_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[1].subject, "POLICE ONLINE PLEA: 06/AA/0000000/00 DOH: {} PUBLIC Joe"
                         .format(self.hearing_date.strftime("%Y-%m-%d")))

    def test_PLP_case_details_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContainsDefinition(response.content, "First name", "Joe", count=1)
        self.assertContainsDefinition(response.content, "Last name", "Public", count=1)



    def test_PLP_single_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContainsDefinition(response.content, "Your plea", "Guilty", count=1)

    def test_PLP_multiple_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()

        context_data["plea"]["data"].append({"guilty_extra": "test2", "guilty": "guilty_no_court"})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContainsDefinition(response.content, "Your plea", "Guilty", count=2)

    def test_PLP_single_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContainsDefinition(response.content, "Your plea", "Not guilty", count=1)

    def test_PLP_multiple_not_guilty_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"][0]["guilty"] = "not_guilty"
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty",
                                             "hearing_language": True, "documentation_language": True})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContainsDefinition(response.content, "Your plea", "Not guilty", count=2)

    def test_PLP_mixed_plea_email_plea_output(self):
        context_data = self.get_context_data()
        context_data["plea"]["data"].append({"not_guilty_extra": "test2", "guilty": "not_guilty",
                                             "hearing_language": True, "documentation_language": True})

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        self.assertContainsDefinition(response.content, "Your plea", "Guilty", count=1)
        self.assertContainsDefinition(response.content, "Your plea", "Not guilty", count=1)

    def test_under_18_message_is_shown_when_user_is_18(self):
        context_data = self.get_context_data()
        context_data["your_details"]["date_of_birth"] = (datetime.today() - relativedelta(years=18)).date()
        send_plea_email(context_data)
        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        assert b"The defendant is 18 years old or under" in response.content

    def test_under_18_message_is_shown_when_user_is_under_18(self):
        context_data = self.get_context_data()
        context_data["your_details"]["date_of_birth"] = (datetime.today() - relativedelta(years=17)).date()
        send_plea_email(context_data)
        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        assert b"The defendant is 18 years old or under" in response.content

    def test_under_18_message_is_not_shown_when_user_over_18(self):
        context_data = self.get_context_data()
        context_data["your_details"]["date_of_birth"] = (datetime.today() - relativedelta(years=19)).date()
        send_plea_email(context_data)
        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        assert b"The defendant is 18 years old or under" not in response.content

    def test_under_18_message_is_not_shown_when_no_date_of_birth_present(self):
        context_data = self.get_context_data()
        del context_data["your_details"]["date_of_birth"]
        send_plea_email(context_data)
        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        assert b"The defendant is 18 years old or under" not in response.content

    def test_under_18_message_is_not_shown_when_bad_date_of_birth_present(self):
        context_data = self.get_context_data()
        context_data["your_details"]["date_of_birth"] = "not a date"
        send_plea_email(context_data)
        response = self.get_mock_response(mail.outbox[1].attachments[0][1])
        assert b"The defendant is 18 years old or under" not in response.content

class DefendantEmailTemplateTests(BaseEmailTemplateTests):
    def test_plea_email_guilty_pleas(self):
        context_data = self.get_context_data()
        context_data["case"]["number_of_pleas"] = 3
        context_data["plea"]["data"] = [
            {
                "guilty": "guilty_no_court",
                "guilty_extra": "asdf"
            },
            {
                "guilty": "guilty_no_court",
                "guilty_extra": "asdf"
            },
            {
                "guilty": "guilty_no_court",
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
                "not_guilty_extra": "asdf",
                "hearing_language": True,
                "documentation_language": True
            },
            {
                "guilty": "not_guilty",
                "not_guilty_extra": "asdf",
                "hearing_language": True,
                "documentation_language": True
            },
            {
                "guilty": "not_guilty",
                "not_guilty_extra": "asdf",
                "hearing_language": True,
                "documentation_language": True
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
                "not_guilty_extra": "asdf",
                "hearing_language": True,
                "documentation_language": True
            },
            {
                "guilty": "guilty_no_court",
                "guilty_extra": "asdf"
            },
            {
                "guilty": "guilty_court",
                "guilty_extra": "asdf",
                "hearing_language": True,
                "documentation_language": True
            }
        ]

        send_plea_email(context_data)

        response = self.get_mock_response(mail.outbox[2].body)

        self.assertContains(response, "<<MIXED>>")

    def test_email_send_with_multiple_unsent_pleas(self):
        data = self.get_context_data()
        case = Case(urn=data["case"]["urn"], sent=False)
        case.save()
        case2 = Case(urn=data["case"]["urn"], sent=False)
        case2.save()

        send_plea_email(data)

    def test_forward_email_section_removed_from_plea_confirmation(self):
        context_data = self.get_context_data()

        send_plea_email(context_data)

        search_text = "If you're unsure an email is from the Ministry of Justice"
        self.assertNotIn(search_text, mail.outbox[2].body)

    def test_forward_email_section_removed_from_sjp_plea_confirmation(self):
        context_data = self.get_context_data(notice_type_data={"sjp": True})

        send_plea_email(context_data)

        search_text = "If you're unsure an email is from the Ministry of Justice"
        self.assertNotIn(search_text, mail.outbox[2].body)


class TestCompanyFinancesEmailLogic(TestCase):
    def setUp(self):
        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 12345678",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            test_mode=True)

        self.test_session_data = {
            "notice_type": {
                "complete": True,
                "sjp": False
            },
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "urn": "06AA000000000",
                "number_of_charges": 1,
                "plea_made_by": "Company representative",
                "contact_deadline": ""
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
                "contact_number": "0800 12345678",
                "email": "user@example.org"
            },
            "plea": {
                "complete": True,
                "data": [
                    {
                        "guilty": "not_guilty",
                        "not_guilty_extra": "something",
                        "hearing_language": True,
                        "documentation_language": True
                    }
                ]
            },
            "your_employment": {
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

        self.test_session_data["plea"]["data"][0]["guilty"] = "guilty_no_court"
        del self.test_session_data["company_finances"]["skipped"]

        send_plea_email(self.test_session_data)

        attachment = mail.outbox[0].attachments[0][1]

        self.assertTrue("<<SHOWCOMPANYDETAILS>>" in attachment)
        self.assertTrue("<<SHOWYOURDETAILS>>" not in attachment)
        self.assertTrue("<<SHOWCOMPANYFINANCES>>" in attachment)
        self.assertTrue("<<SHOWEXPENSES>>" not in attachment)
