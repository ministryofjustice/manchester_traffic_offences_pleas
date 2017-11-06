from importlib import import_module

from django.conf import settings
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.template.context import RequestContext
from django.utils.translation import activate

from mock import Mock
from waffle.models import Switch

from ..views import PleaOnlineForms
from ..models import CourtEmailCount, Court


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

    def get_request_mock(self, url="/", url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request


class TestLanguageSwitcher(TestCase):
    def setUp(self):
        self.client = Client()
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_language_switcher_lang_cy(self):
        Switch.objects.create(name="show_language_switcher", active=True)

        response = self.client.get("/change-language/?lang=cy")
        response = self.client.get("/")

        self.assertContains(response, 'hreflang="en" lang="en"')
        self.assertNotContains(response, 'hreflang="cy" lang="cy"')

    def test_language_switcher_lang_en(self):
        Switch.objects.create(name="show_language_switcher", active=True)

        response = self.client.get("/change-language/?lang=en")
        response = self.client.get("/")

        self.assertContains(response, 'hreflang="cy" lang="cy"')
        self.assertNotContains(response, 'hreflang="en" lang="en"')


class TestLanguage(TestMultiPleaFormBase):
    def setUp(self):
        self.create_court()
        self.client = Client()
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        self.session["plea_data"] = {
            "notice_type": {
                "complete": True,
                "sjp": False
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
                "middle_name": "",
                "last_name": "Brown",
                "contact_number": "07802639892"
            },
            "plea": {
                "data": [
                    {
                        "guilty": "guilty_no_court",
                        "guilty_extra": "something",
                        "complete": True,
                    },
                    {
                        "guilty": "guilty_no_court",
                        "guilty_extra": "something",
                        "complete": True,
                    },
                    {
                        "guilty": "guilty_no_court",
                        "guilty_extra": "something",
                        "complete": True,
                    }
                ]
            },
            "your_employment": {
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

    def test_cy_stored_in_stats(self):
        activate("cy-GB")

        fake_request = self.get_request_mock("/plea/review")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(self.session["plea_data"], "review")
        form.save({"receive_email_updates": True,
                   "email": "user@example.org",
                   "understand": True},
                  request_context)
        response = form.render(self.get_request_mock())
        self.assertEqual(response.status_code, 302)

        c = list(CourtEmailCount.objects.all())
        self.assertEqual(c[0].language, "cy")

    def test_en_stored_in_stats(self):
        activate("en-GB")

        fake_request = self.get_request_mock("/plea/review")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(self.session["plea_data"], "review")
        form.save({"receive_email_updates": True,
                   "email": "user@example.org",
                   "understand": True},
                  request_context)
        response = form.render(self.get_request_mock())
        self.assertEqual(response.status_code, 302)

        c = list(CourtEmailCount.objects.all())
        self.assertEqual(c[0].language, "en")
