from django.test import TestCase

from plea.forms import AboutForm

about_data_valid = {
    'date_of_hearing': '01/01/1977',
    'urn': '00/AA/0000000/00',
    'name': 'John Smith',
}

about_data_invalid = {
    'date_of_hearing': 'AA/BB/CC',
    'urn': '00/AA/',
    'name': '',
}

class TestPleaFormWizzad(TestCase):
    
    def test_about_form_valid(self):
        f = AboutForm(about_data_valid)
        self.assertTrue(f.is_valid())
        self.assertFalse(f.errors)

    def test_about_form_invalid(self):
        f = AboutForm(about_data_invalid)
        self.assertFalse(f.is_valid())
        self.assertTrue('date_of_hearing' in f.errors)
        self.assertTrue('name' in f.errors)
        self.assertTrue('urn' in f.errors)
