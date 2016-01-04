from django.test import TestCase
from django.test.client import RequestFactory
from django.template.context import RequestContext

from mock import Mock

from ..views import PleaOnlineForms
from ..models import CourtEmailCount, Court, Case


class TestMultiPleaFormBase(TestCase):

    def create_court(self):
        self.court = Court.objects.create(
            court_code="0000",
            region_code="51",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            test_mode=False)

    def get_request_mock(self, url, url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request


class TestSJP(TestMultiPleaFormBase):
    def setUp(self):
        self.create_court()
        self.session = {
            "notice_type": {
                "complete": True,
                "sjp": True
            },
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "contact_deadline": "2015-01-01",
                "urn": "51AA000000000",
                "number_of_charges": 3,
                "plea_made_by": "Defendant"
            },
            "your_details": {
                "complete": True,
                "first_name": "Charlie",
                "last_name": "Brown",
                "contact_number": "07802639892"
            },
            "plea": {
                "data": [
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something",
                        "complete": True,
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something",
                        "complete": True,
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something",
                        "complete": True,
                    }
                ]
            },
            "your_finances": {
                "complete": True,
                "you_are": "Employed",
                "employer_name": "test",
                "employer_address": "test",
                "employer_phone": "test",
                "take_home_pay_period": "Fortnightly",
                "take_home_pay_amount": "1000",
                "employer_hardship": True
            },
            "hardship": {
                "complete": True
            },
            "household_expenses": {
                "complete": True
            },
            "other_expenses": {
                "complete": True
            },
            "your_expenses": {
                "total_household_expenses": 999
            },
        }

    def test_sjp_field_true(self):
        fake_request = self.get_request_mock("/plea/review")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(self.session, "review")
        form.save({"receive_email_updates": True,
                   "email": "user@example.org",
                   "understand": True},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        # Check SJP is in the count table
        c = list(CourtEmailCount.objects.all())
        self.assertEqual(c[0].initiation_type, "J")

        # Check SJP is in the case table
        c = list(Case.objects.all())
        self.assertEqual(c[0].initiation_type, "J")

    def test_sjp_field_false(self):
        fake_request = self.get_request_mock("/plea/review")
        request_context = RequestContext(fake_request)

        self.session.update({"notice_type": {"sjp": False}})

        form = PleaOnlineForms(self.session, "review")
        form.save({"receive_email_updates": True,
                   "email": "user@example.org",
                   "understand": True},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        # Check SJP is in the count table
        c = list(CourtEmailCount.objects.all())
        self.assertEqual(c[0].initiation_type, "Q")

        # Check SJP is in the count table
        c = list(Case.objects.all())
        self.assertEqual(c[0].initiation_type, "Q")
