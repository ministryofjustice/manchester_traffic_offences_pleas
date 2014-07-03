import datetime
from mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse

from plea.forms import AboutForm
from plea.views import PleaOnlineForms


about_data_valid = {
    'date_of_hearing': '01/01/1977',
    'urn': '00/AA/0000000/00',
    'name': 'John Smith',
    'number_of_charges': 1
}

about_data_invalid = {
    'date_of_hearing': 'AA/BB/CC',
    'urn': '00/AA/',
    'name': '',
    'number_of_charges': 1
}


class TestMultiPleaForms(TestCase):
    def test_successful_completion_single_charge(self):
        fake_session = {}
        request_context = {}

        form = PleaOnlineForms("about", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"date_of_hearing": "2015-01-01",
                              "urn": "00/AA/0000000/00",
                              "name": "Charlie Brown",
                              "number_of_charges": "2"},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("plea", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"guilty": "guilty",
                              "mitigations": "lorem ipsum",
                              "understand": "True"},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("review", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("complete", "plea_form_step", fake_session)
        response = form.load(request_context)

        self.assertEqual(fake_session["date_of_hearing"], datetime.date(2015, 1, 1))
        self.assertEqual(fake_session["urn"], "00/AA/0000000/00")
        self.assertEqual(fake_session["name"], "Charlie Brown")
        self.assertEqual(fake_session["number_of_charges"], 2)
        self.assertEqual(fake_session["guilty"], "guilty")
        self.assertEqual(fake_session["mitigations"], "lorem ipsum")
        self.assertEqual(fake_session["understand"], True)

    def successful_completion_multiple_charges(self):
        pass


class TestPleaFormWizzad(TestCase):
    
    def test_about_form_valid(self):
        f = AboutForm(about_data_valid)
        result = f.is_valid()
        self.assertTrue(result)
        self.assertFalse(f.errors)

    def test_about_form_invalid(self):
        f = AboutForm(about_data_invalid)
        self.assertFalse(f.is_valid())
        self.assertTrue('date_of_hearing' in f.errors)
        self.assertTrue('name' in f.errors)
        self.assertTrue('urn' in f.errors)


