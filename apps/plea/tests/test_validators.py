from django.test import TestCase
from django import forms
from ..fields import is_valid_urn_format


class UtilsTestCase(TestCase):
    urls = 'defendant.tests.urls'

    def test_is_valid_urn_format(self):
        good_urns = [
            "00/AA/0000000/00",
            "12/bb/1234567/12",
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
        ]

        for URN in good_urns:
            self.assertTrue(is_valid_urn_format(URN))

        for URN in bad_urns:
            with self.assertRaises(forms.ValidationError):
                is_valid_urn_format(URN)
