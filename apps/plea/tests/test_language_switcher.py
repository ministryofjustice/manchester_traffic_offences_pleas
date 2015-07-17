from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from importlib import import_module

from waffle.models import Switch

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


    def test_language_switcher_waffle_switch_off(self):
        response = self.client.get("/")

        self.assertNotContains(response, '<nav class="language-switcher">')

    def test_language_switcher_waffle_switch_on(self):
        Switch.objects.create(name="show_language_switcher", active=True)

        response = self.client.get("/")

        self.assertContains(response, '<nav class="language-switcher">')


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
