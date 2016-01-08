from datetime import datetime

from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import RequestFactory
from mock import Mock

from make_a_plea.serializers import DateAwareSerializer

from views import start


class DateAwareSerializerTests(TestCase):
    def test_serializer_dumps_plain(self):
        test_str = """{"key2": 2, "key1": "value1"}"""
        test_dict = {"key1": "value1",
                     "key2": 2}

        ds = DateAwareSerializer().dumps(test_dict)
        self.assertEqual(ds, test_str)

    def test_serializer_loads_plain(self):
        test_str = """{"key2": 2, "key1": "value1"}"""
        test_dict = {"key1": "value1",
                     "key2": 2}

        ds = DateAwareSerializer().loads(test_str)
        self.assertEqual(ds, test_dict)

    def test_serializer_dumps_datetime(self):
        test_str = """{"key2": "2014-06-03T00:00:00", "key1": "value1"}"""
        test_dict = {"key1": "value1",
                     "key2": datetime(2014, 6, 3, 0, 0)}

        ds = DateAwareSerializer().dumps(test_dict)
        self.assertEqual(ds, test_str)


class TestStartRedirect(TestCase):

    def get_request_mock(self, url, url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request

    @override_settings(REDIRECT_START_PAGE="http://redirect.test")
    def test_start_screen_redirects(self):
        fake_request = self.get_request_mock("/")

        response = start(fake_request)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "http://redirect.test")

    def test_start_screen_does_not_redirect(self):
        fake_request = self.get_request_mock("/")

        response = start(fake_request)

        self.assertEquals(response.status_code, 200)
