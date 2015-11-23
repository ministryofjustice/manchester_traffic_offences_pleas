from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from importlib import import_module

from waffle.models import Switch


class TestAccessibilitySwitcher(TestCase):

    def setUp(self):
        self.client = Client()
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_a11y_testing_waffle_switch_off(self):
        response = self.client.get("/set-a11y-testing/")

        self.assertEqual(response.status_code, 404)

    def test_a11y_testing_mode_tota11y(self):
        Switch.objects.create(name="enable_a11y_testing", active=True)

        response = self.client.get("/set-a11y-testing/?mode=tota11y")
        response = self.client.get("/")

        self.assertContains(response, "/static/javascripts/vendor/tota11y.min.js")

    def test_a11y_testing_mode_google(self):
        Switch.objects.create(name="enable_a11y_testing", active=True)

        response = self.client.get("/set-a11y-testing/?mode=google")
        response = self.client.get("/")

        self.assertContains(response, "/static/javascripts/vendor/axs_testing.js")

    def test_a11y_testing_mode_off(self):
        Switch.objects.create(name="enable_a11y_testing", active=True)

        response = self.client.get("/set-a11y-testing/?mode=off")
        response = self.client.get("/")

        self.assertNotContains(response, "/static/javascripts/vendor/tota11y.min.js")
        self.assertNotContains(response, "/static/javascripts/vendor/axs_testing.js")

    def test_a11y_testing_mode_wrong(self):
        Switch.objects.create(name="enable_a11y_testing", active=True)

        response = self.client.get("/set-a11y-testing/?mode=gfhdjaks")
        response = self.client.get("/")

        self.assertNotContains(response, "/static/javascripts/vendor/tota11y.min.js")
        self.assertNotContains(response, "/static/javascripts/vendor/axs_testing.js")
