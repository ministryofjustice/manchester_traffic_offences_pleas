from collections import OrderedDict
from django.test import TestCase
from mock import Mock
from django.test.client import RequestFactory
from django.template.context import RequestContext

from ..views import PleaOnlineForms
from ..stages import calculate_weekly_amount, YourBenefitsStage

class TestCalculations(TestCase):
    def test_calculate_weekly_amount(self):
        amount = calculate_weekly_amount(130, "Weekly")

        self.assertEqual(amount, 130)

    def test_calculate_fortnightly_amount(self):
        amount = calculate_weekly_amount(130, "Fortnightly")

        self.assertEqual(amount, 65)

    def test_calculate_monthly_amount(self):
        amount = calculate_weekly_amount(130, "Monthly")

        self.assertEqual(amount, 30)


class TestIncomeBaseStage(TestCase):
    def setUp(self):
        self.urls = OrderedDict((("your_benefits", "your_benefits"),))

    def test_add_income_source(self):
        test_stage = YourBenefitsStage(self.urls, {"your_income": {}})

        test_stage.add_income_source("Label", "Weekly", 130)

        self.assertEqual(len(test_stage.all_data["your_income"]["sources"]), 1)
        self.assertEqual(test_stage.all_data["your_income"]["sources"]["your_benefits"]["label"], "Label")
        self.assertEqual(test_stage.all_data["your_income"]["sources"]["your_benefits"]["pay_period"], "Weekly")
        self.assertEqual(test_stage.all_data["your_income"]["sources"]["your_benefits"]["pay_amount"], 130)
        self.assertEqual(test_stage.all_data["your_income"]["weekly_total"], 130)

    def test_remove_income_source(self):
        test_stage = YourBenefitsStage(self.urls, {"your_income": {"sources": {"your_employment": {}}}})

        test_stage.remove_income_sources(["your_employment"])

        self.assertEqual(len(test_stage.all_data["your_income"]["sources"]), 0)


class TestYourIncomeStages(TestCase):
    def get_request_mock(self, url, url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request

    def setUp(self):
        self.fake_session = {"notice_type": {"complete": True},
                             "case": {"complete": True},
                             "your_details": {"complete": True},
                             "plea": {"complete": True}}

        self.fake_request = self.get_request_mock("/plea/your_status/")
        self.request_context = RequestContext(self.fake_request)

    def test_your_income_employed_weekly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_employment")
        form.load(self.request_context)

        form.save({"pay_period": "Weekly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 1)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["label"], "Employment")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["pay_period"], "Weekly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 130)

    def test_your_income_employed_fortnightly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_employment")
        form.load(self.request_context)

        form.save({"pay_period": "Fortnightly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 1)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["label"], "Employment")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["pay_period"], "Fortnightly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 65)

    def test_your_income_employed_monthly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_employment")
        form.load(self.request_context)

        form.save({"pay_period": "Monthly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 1)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["label"], "Employment")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["pay_period"], "Monthly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_employment"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 30)

    def test_your_income_self_employed_other(self):
        self.fake_session.update({"your_status": {"you_are": "Self-employed",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_self_employment")
        form.load(self.request_context)

        form.save({"pay_period": "Other",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 1)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_self_employment"]["label"], "Self-employment")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_self_employment"]["pay_period"], "Weekly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_self_employment"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 130)

    def test_your_income_employed_with_benefits_weekly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed and also receiving benefits",
                                                  "complete": True},
                                  "your_income": {"sources": {"your_employment": {"pay_period": "Weekly",
                                                                                  "pay_amount": 130}}}})

        form = PleaOnlineForms(self.fake_session, "your_benefits")
        form.load(self.request_context)

        form.save({"benefit_type": "Income Support",
                   "pay_period": "Weekly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 2)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["label"], "Benefits")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["benefit_type"], "Income Support")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["pay_period"], "Weekly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 260)

    def test_your_income_employed_with_benefits_fortnightly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed and also receiving benefits",
                                                  "complete": True},
                                  "your_income": {"sources": {"your_employment": {"pay_period": "Weekly",
                                                                                  "pay_amount": 130}}}})

        form = PleaOnlineForms(self.fake_session, "your_benefits")
        form.load(self.request_context)

        form.save({"benefit_type": "Income Support",
                   "pay_period": "Fortnightly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 2)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["label"], "Benefits")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["benefit_type"], "Income Support")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["pay_period"], "Fortnightly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 195)

    def test_your_income_employed_with_benefits_monthly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed and also receiving benefits",
                                                  "complete": True},
                                  "your_income": {"sources": {"your_employment": {"pay_period": "Weekly",
                                                                                  "pay_amount": 130}}}})

        form = PleaOnlineForms(self.fake_session, "your_benefits")
        form.load(self.request_context)

        form.save({"benefit_type": "Income Support",
                   "pay_period": "Monthly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 2)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["label"], "Benefits")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["benefit_type"], "Income Support")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["pay_period"], "Monthly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_benefits"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 160)

    def test_your_income_benefits_weekly(self):
        self.fake_session.update({"your_status": {"you_are": "Receiving out of work benefits",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_out_of_work_benefits")
        form.load(self.request_context)

        form.save({"benefit_type": "Contributory Jobseeker's Allowance",
                   "pay_period": "Weekly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 1)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_out_of_work_benefits"]["label"], "Benefits")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_out_of_work_benefits"]["benefit_type"], "Contributory Jobseeker's Allowance")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_out_of_work_benefits"]["pay_period"], "Weekly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_out_of_work_benefits"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 130)

    def test_your_income_other_weekly(self):
        self.fake_session.update({"your_status": {"you_are": "Other",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "about_your_income")
        form.load(self.request_context)

        form.save({"income_source": "Student loan",
                   "pay_period": "Weekly",
                   "pay_amount": 130,
                   "pension_credit": False},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 1)
        self.assertEqual(self.fake_session["your_income"]["sources"]["about_your_income"]["label"], "Student loan")
        self.assertEqual(self.fake_session["your_income"]["sources"]["about_your_income"]["pay_period"], "Weekly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["about_your_income"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 130)

    def test_your_income_other_with_pension_credit_weekly(self):
        self.fake_session.update({"your_status": {"you_are": "Other",
                                                  "complete": True,
                                  "your_income": {"sources": {"about_your_income": {"pay_period": "Weekly",
                                                                                    "pay_amount": 130}}}}})

        form = PleaOnlineForms(self.fake_session, "your_pension_credit")
        form.load(self.request_context)

        form.save({"pay_period": "Weekly",
                   "pay_amount": 130},
                  self.request_context)

        self.assertEqual(len(self.fake_session["your_income"]["sources"]), 1)
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_pension_credit"]["label"], "Pension Credit")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_pension_credit"]["pay_period"], "Weekly")
        self.assertEqual(self.fake_session["your_income"]["sources"]["your_pension_credit"]["pay_amount"], 130)
        self.assertEqual(self.fake_session["your_income"]["weekly_total"], 130)

