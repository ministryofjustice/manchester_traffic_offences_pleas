import random
import string
from datetime import datetime, timedelta

from django.test import TestCase, Client
from django.test.utils import override_settings
from django.test.client import RequestFactory
from django.conf import settings
from django.contrib.auth.models import User

from mock import Mock

from make_a_plea.serializers import DateAwareSerializer
from apps.plea.models import Case, Offence
from apps.result.models import Result, ResultOffence, ResultOffenceData
from .views import start

from .management.commands.delete_old_data import Command


def yield_waffle(chars=7, words=1, lines=1):
    """Produce lorem ipsum text in an iterable form."""

    for line, lindex in enumerate(range(lines)):
        for word, windex in enumerate(range(words)):
            for char, cindex in enumerate(range(chars)):

                if not cindex:  # Capitalise first character
                    yield random.choice(string.uppercase)
                else:
                    yield random.choice(string.lowercase)

            if all([
                words > 1,  # No space after if only one word
                windex + 1 < words,  # No space after last word
            ]):
                yield " "

        if all([
            lines > 1,  # No newline if only one line
            lindex + 1 < lines,  # No newline after last line
        ]):
            yield r"\r\n"


class DateAwareSerializerTests(TestCase):
    def test_serializer_dumps_plain(self):
        test_str = b"""{"key1": "value1", "key2": 2}"""
        test_dict = {"key1": "value1",
                     "key2": 2}

        ds = DateAwareSerializer().dumps(test_dict)
        self.assertEqual(ds.decode(), test_str.decode())

    def test_serializer_loads_plain(self):
        test_str = b"""{"key1": "value1", "key2": 2}"""
        test_dict = {"key1": "value1",
                     "key2": 2}

        ds = DateAwareSerializer().loads(test_str)
        self.assertEqual(ds.items(), test_dict.items())

    def test_serializer_dumps_datetime(self):
        test_str = b"""{"key1": "value1", "key2": "2014-06-03T00:00:00"}"""
        test_dict = {"key1": "value1",
                     "key2": datetime(2014, 6, 3, 0, 0)}

        ds = DateAwareSerializer().dumps(test_dict)
        self.assertEqual(ds.decode(), test_str.decode())


class TestStartRedirect(TestCase):

    def get_request_mock(self, url="/", url_name="", url_kwargs=None):
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


class CullOldDataTestCase(TestCase):

    def setUp(self):
        self.command = Command()

    def _make_case(self, created_date):
        case = Case.objects.create(urn="51xx0000000")

        Offence.objects.create(case=case)

        case.created = created_date
        case.save()

    def _make_result(self, created_date):
        result = Result.objects.create(urn="51xx0000000",
                                       date_of_hearing="2016-08-08")

        offence = ResultOffence.objects.create(result=result)

        ResultOffenceData.objects.create(result_offence=offence)

        result.created = created_date
        result.save()

    def test_old_records_are_deleted(self):

        created_date = datetime.now() - timedelta(settings.DATA_RETENTION_PERIOD + 1)

        self._make_case(created_date)
        self._make_result(created_date)

        self.command.handle()

        self.assertEquals(Case.objects.count(), 0)
        self.assertEquals(Offence.objects.count(), 0)
        self.assertEquals(Result.objects.count(), 0)
        self.assertEquals(ResultOffence.objects.count(), 0)
        self.assertEquals(ResultOffenceData.objects.count(), 0)

    def test_newer_records_are_retained(self):

        created_date = datetime.now() - timedelta(settings.DATA_RETENTION_PERIOD - 1)

        self._make_case(created_date)
        self._make_result(created_date)

        self.command.handle()

        self.assertEquals(Case.objects.count(), 1)
        self.assertEquals(Result.objects.count(), 1)


class TestAdminPanel(TestCase):
    """From https://tommorris.org/posts/9389"""

    def create_user(self):
        self.username = "test_admin"
        self.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=self.username)
        user.set_password(self.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.user = user

    def test_spider_admin(self):
        self.create_user()
        client = Client()
        client.login(username=self.username, password=self.password)
        admin_pages = [
            "/admin/",
            "/admin/auth/",
            "/admin/auth/group/",
            "/admin/auth/group/add/",
            "/admin/auth/user/",
            "/admin/auth/user/add/",
            "/admin/password_change/",
            "/admin/plea/auditevent/",
            "/admin/plea/case/",
            "/admin/result/result/",
        ]
        for page in admin_pages:
            resp = client.get(page)
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, "<!DOCTYPE html")
