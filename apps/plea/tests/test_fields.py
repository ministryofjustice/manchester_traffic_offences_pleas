import datetime as dt

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..fields import is_urn_not_used
from ..models import CourtEmailPlea


class TestUrnValidators(TestCase):

    def setUp(self):
        self.plea = CourtEmailPlea(urn="00/AA/000000/00",
                                   hearing_date=dt.datetime.now())

        self.plea.save()

    def test_is_urn_not_used_with_existing_urn_but_not_sent_status(self):
        self.assertTrue(is_urn_not_used("00/AA/000000/00"))

    def test_is_urn_not_used_with_existing_urn_and_sent_status(self):
        self.plea.status = "sent"
        self.plea.save()

        with self.assertRaises(ValidationError):
            is_urn_not_used("00/AA/000000/00")

    def test_is_urn_not_used_case_insensitive(self):
        self.plea.status = "sent"
        self.plea.save()

        with self.assertRaises(ValidationError):
            is_urn_not_used("00/aa/000000/00")

    def test_is_urn_not_used_with_no_existing_urn(self):
        self.plea.delete()

        self.assertTrue(is_urn_not_used("00/AA/000000/00"))




