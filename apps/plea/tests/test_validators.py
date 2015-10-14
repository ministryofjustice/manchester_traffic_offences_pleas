from datetime import date, timedelta

from django.test import TestCase
from django import forms
from django.forms import ValidationError

from ..models import Court, Case
from ..validators import *


class TestValidators(TestCase):
    urls = 'defendant.tests.urls'

    def setUp(self):
        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="test@test.com",
            submission_email="test@test.com",
            plp_email="test@test.com",
            enabled=True,
            test_mode=False)

    def test_urn_valid_database(self):
        self.court.validate_urn = True
        self.court.save()

        case = Case(urn="06/QQ/00000/00", sent=False)
        case.save()

        self.assertTrue(is_urn_valid("06/QQ/00000/00"))

    def test_urn_invalid_database(self):
        self.court.validate_urn = True
        self.court.save()

        with self.assertRaises(ValidationError):
            is_urn_valid("06/QQ/00000/01")

    def test_is_valid_urn_format(self):
        good_urns = [
            "06/AA/12345/99",
            "06/AA/0012345/99",
            "06/bb/1234567/12",
            "06/JJ/50563/14",
            "06/JJ/50534/14",
            "06AB/12345/99",
            "06AB12345/99",
            "06AB123456711"
        ]
        bad_urns = [
            "123",
            "AAA",
            "0/BB/12345/99",
            "0/BB/0012345/99",
            "06/B/12345/99",
            "06/BB/1234/99",
            "06/BB/123456/99",
            "06/BB/12345/9",
            "06/BB/1234567/9"
        ]

        for URN in good_urns:
            self.assertTrue(is_urn_valid(URN))

        for URN in bad_urns:
            with self.assertRaises(forms.ValidationError):
                is_urn_valid(URN)


    def test_date_is_in_past(self):
        yesterday = date.today() - timedelta(1)

        self.assertTrue(is_date_in_past(yesterday))

    def test_date_is_not_in_past(self):
        tomorrow = date.today() + timedelta(1)

        with self.assertRaises(forms.ValidationError):
            is_date_in_past(tomorrow)

    def test_date_is_in_future(self):
        tomorrow = date.today() + timedelta(1)

        self.assertTrue(is_date_in_future(tomorrow))

    def test_date_is_not_in_future(self):
        yesterday = date.today() - timedelta(1)

        with self.assertRaises(forms.ValidationError):
            is_date_in_future(yesterday)

    def test_date_is_in_last_28_days(self):
        yesterday = date.today() - timedelta(1)

        self.assertTrue(is_date_in_last_28_days(yesterday))

    def test_date_is_not_in_last_28_days(self):
        more_than_28_days_ago = date.today() - timedelta(30)

        with self.assertRaises(forms.ValidationError):
            is_date_in_last_28_days(more_than_28_days_ago)

    def test_date_is_in_next_6_months(self):
        tomorrow = date.today() + timedelta(1)

        self.assertTrue(is_date_in_next_6_months(tomorrow))

    def test_date_is_not_in_next_6_months(self):
        more_than_6_months_from_now = date.today() + timedelta(200)

        with self.assertRaises(forms.ValidationError):
            is_date_in_next_6_months(more_than_6_months_from_now)
