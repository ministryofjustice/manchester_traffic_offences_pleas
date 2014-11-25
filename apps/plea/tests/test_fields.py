import datetime as dt

from django.core.exceptions import ValidationError
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from ..fields import is_urn_not_used
from ..models import CourtEmailPlea, Case


class TestUrnValidator(TestCase):

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


class TestFullUrnValidator(TestCase):

    def setUp(self):
        self.case = Case.objects.create(name="Willie Wonka",
                                        hearing_date=dt.date(2014, 10, 01),
                                        urn="00/AA/00000/00")

        self.plea = CourtEmailPlea.objects.create(
            urn="00/A1/000000/00",
            hearing_date=dt.datetime.now())

    @override_settings(SWITCH_FULL_URN_VALIDATION=True)
    def test_urn_does_not_match_case(self):

        with self.assertRaises(ValidationError):
            is_urn_not_used("00/BB/000000/00")

    @override_settings(SWITCH_FULL_URN_VALIDATION=True)
    def test_urn_matches_case(self):
        Case.objects.create(urn="00/AA/00000/00", hearing_date=dt.datetime.now())
        self.assertTrue(is_urn_not_used("00/AA/00000/00"))

    @override_settings(SWITCH_FULL_URN_VALIDATION=True)
    def test_urn_matches_case_with_existing_submission(self):
        self.plea.urn = self.case.urn
        self.plea.status = "sent"
        self.plea.save()

        with self.assertRaises(ValidationError):
            is_urn_not_used(self.plea.urn)








