from django.test import TestCase
from mock import Mock
from django.test.client import RequestFactory
from django.template.context import RequestContext

from ..views import PleaOnlineForms

class TestYourIncomeStage(TestCase):
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

        form.save({"pay_frequency": "Weekly",
                   "pay_amount": 120},
                  self.request_context)

        self.assertEqual(self.fake_session["your_income"]["income_frequency"], "Weekly")
        self.assertEqual(self.fake_session["your_income"]["income_amount"], 120)
        self.assertEqual(self.fake_session["your_income"]["total_weekly_income"], 120)

    def test_your_income_employed_fortnightly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_employment")
        form.load(self.request_context)

        form.save({"pay_frequency": "Fornightly",
                   "pay_amount": 120},
                  self.request_context)

        self.assertEqual(self.fake_session["your_income"]["income_frequency"], "Fornightly")
        self.assertEqual(self.fake_session["your_income"]["income_amount"], 120)
        self.assertEqual(self.fake_session["your_income"]["total_weekly_income"], 60)

    def test_your_income_employed_monthly(self):
        self.fake_session.update({"your_status": {"you_are": "Employed",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_employment")
        form.load(self.request_context)

        form.save({"pay_frequency": "Monthly",
                   "pay_amount": 1300},
                  self.request_context)

        self.assertEqual(self.fake_session["your_income"]["income_frequency"], "Monthly")
        self.assertEqual(self.fake_session["your_income"]["income_amount"], 1300)
        self.assertEqual(self.fake_session["your_income"]["total_weekly_income"], 300)

    def test_your_income_self_employed_other(self):
        self.fake_session.update({"your_status": {"you_are": "Self-employed",
                                                  "complete": True}})

        form = PleaOnlineForms(self.fake_session, "your_self_employment")
        form.load(self.request_context)

        form.save({"pay_frequency": "Other",
                   "pay_amount": 120},
                  self.request_context)

        self.assertEqual(self.fake_session["your_income"]["income_frequency"], "Other")
        self.assertEqual(self.fake_session["your_income"]["income_amount"], 120)
        self.assertEqual(self.fake_session["your_income"]["total_weekly_income"], 120)

