import datetime as dt

from django.core.exceptions import ValidationError
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from ..fields import is_urn_not_used
from ..models import Case


class TestUrnValidator(TestCase):

    def setUp(self):
        self.case = Case.objects.create(urn="00/AA/00000/00", sent=True)

    def test_urn_does_not_match(self):

        self.assertTrue(is_urn_not_used("00/BB/000000/00"))

    def test_urn_matches_but_case_not_sent_or_error(self):

        self.case.status = "created_not_sent"
        self.case.save()

        self.assertTrue(is_urn_not_used("00/AA/000000/00"))

        self.case.status = "network_error"
        self.case.save()

        self.assertTrue(is_urn_not_used("00/AA/000000/00"))

    def test_urn_matches(self):
        with self.assertRaises(ValidationError):
            self.assertTrue(is_urn_not_used("00/AA/00000/00"))







