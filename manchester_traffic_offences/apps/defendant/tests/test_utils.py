from django.test import TestCase
from django import forms
from defendant.utils import is_valid_urn_format


class UtilsTestCase(TestCase):
    urls = 'defendant.tests.urls'
    
    def test_is_valid_urn_format(self):
        good_URNs = [
            "00/AA/0000000/00",
            "12/bb/1234567/12",
        ]
        bad_URNs = [
            "123",
            "00bb/0000000/00",
            "AA/bb/0000000/00",
            "00/bb/000000/00",
            "0/bb/0000000/00",
            "00/bb/0000000/0",
        ]
        
        for URN in good_URNs:
            self.assertTrue(is_valid_urn_format(URN))
        
        for URN in bad_URNs:
            with self.assertRaises(forms.ValidationError):
                is_valid_urn_format(URN)