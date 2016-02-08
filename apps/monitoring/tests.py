from contextlib import contextmanager
from mock import patch
import json
import unittest

from django.test import Client

from requests.exceptions import RequestException


class HealthCheckTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @contextmanager
    def _patch(self, response, exclude=None):
        exclude = exclude or []

        location = "apps.monitoring.views."

        check_methods = [
            "check_mandrill",
            "check_address",
            "check_url",
            "check_database"]

        patches = []

        for method in check_methods:
            if method not in exclude:
                patched = patch(location+method)
                mock = patched.start()
                mock.return_value = response
                patches.append(patched)

        try:
            yield

        finally:
            for patched in patches:
                patched.stop()

    def test_all_ok(self):

        with self._patch(True):
            response = self.client.get("/healthcheck")

        output = json.loads(response.content)

        self.assertEquals(response.status_code, 200)

        self.assertTrue(output["api"]["ok"])
        self.assertTrue(output["database"]["ok"])
        self.assertTrue(output["dashboard"]["ok"])
        self.assertTrue(output["mandrill"]["ok"])

        self.assertTrue(output["ok"])

    @patch("apps.monitoring.check_methods.os.system")
    def test_ping_failure(self, sys_mock):

        sys_mock.return_value = 1

        with self._patch(True, exclude=["check_address", "check_mandrill"]):
            response = self.client.get("/healthcheck")

        output = json.loads(response.content)

        self.assertFalse(output["mandrill"]["ok"])
        self.assertFalse(output["ok"])

    @patch("apps.monitoring.check_methods.requests.get")
    def test_url_failure(self, requests_mock):

        requests_mock.side_effect = RequestException("broken")

        with self._patch(True, exclude=["check_url"]):
            response = self.client.get("/healthcheck")

        output = json.loads(response.content)

        self.assertFalse(output["api"]["ok"])
        self.assertFalse(output["dashboard"]["ok"])
        self.assertFalse(output["ok"])

    @patch("apps.monitoring.check_methods.Case.objects.all")
    def test_database_failure(self, model):

        model.side_effect = Exception("DB error")

        with self._patch(True, exclude=["check_database"]):
            response = self.client.get("/healthcheck")

        output = json.loads(response.content)

        self.assertFalse(output["database"]["ok"])
        self.assertFalse(output["ok"])
