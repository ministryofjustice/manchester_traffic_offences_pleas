from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from importlib import import_module

from ..middleware import TimeoutRedirectMiddleware

class TestTimeout(TestCase):

    def setUp(self):
        self.client = Client()
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = "django.contrib.sessions.backends.file"
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_no_urn_no_refresh_headers(self):
        response = self.client.get("/plea/case/")

        self.assertEqual(response.has_header("Refresh"), False)

    def test_no_session_in_request(self):
        request = {}
        response = {}
        mw = TimeoutRedirectMiddleware()

        response = mw.process_response(request, response)
        self.assertTrue(len(response.keys()) == 0)

    def test_when_urn_has_refresh_headers(self):
        session = self.session
        session["plea"] = {}
        session["plea"]["case"] = {"urn": "51/AA/00000/00"}
        session.save()

        response = self.client.get("/plea/case/")

        wait = str(getattr(settings, "SESSION_COOKIE_AGE", 3600));

        self.assertEqual(response.has_header("Refresh"), True)
        self.assertTrue("Refresh: " + wait + "; url=/session-timeout/" in response.serialize_headers())
