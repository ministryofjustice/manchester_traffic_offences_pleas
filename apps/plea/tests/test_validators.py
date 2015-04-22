from django.test import TestCase
from django import forms

from ..models import Court
from ..fields import is_urn_valid


class UtilsTestCase(TestCase):
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

    def test_is_valid_urn_format(self):
        good_urns = [
            "06/AA/0000000/00",
            "06/bb/1234567/12",
            "06/JJ/50563/14",
            "06/JJ/50534/14",
        ]
        bad_urns = [
            "123",
            "00bb/0000000/00",
            "AA/bb/0000000/00",
            "00/bb/000000/00",
            "0/bb/0000000/00",
            "00/bb/0000000/0",
            "00/aa/00000/00"
        ]

        for URN in good_urns:
            self.assertTrue(is_urn_valid(URN))

        for URN in bad_urns:
            with self.assertRaises(forms.ValidationError):
                is_urn_valid(URN)
