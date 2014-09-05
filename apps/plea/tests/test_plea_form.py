import datetime
from mock import Mock

from django.test import TestCase
from django.test.client import RequestFactory
from django.template.context import RequestContext

from ..views import PleaOnlineForms


class TestMultiPleaForms(TestCase):
    def setUp(self):
        self.session = {}
        self.request_context = {}

        self.plea_stage_pre_data_1_charge = {"case": {"date_of_hearing": "2015-01-01",
                                                      "urn_0": "00",
                                                      "urn_1": "AA",
                                                      "urn_2": "0000000",
                                                      "urn_3": "00",
                                                      "number_of_charges": "1"},
                                             "your_details": {"name": "Charlie Brown",
                                                              "contact_number": "012345678",
                                                              "email": "charliebrown@example.org"}}

        self.plea_stage_pre_data_3_charges = {"case": {"date_of_hearing": "2015-01-01",
                                                       "urn_0": "00",
                                                       "urn_1": "AA",
                                                       "urn_2": "0000000",
                                                       "urn_3": "00",
                                                       "number_of_charges": "3"},
                                              "your_details": {"name": "Charlie Brown",
                                                               "contact_number": "012345678",
                                                               "email": "charliebrown@example.org"}}

        self.request_factory = RequestFactory()

    def get_request_mock(self, url, url_name="", url_kwargs=None):
        if not url_kwargs:
            url_kwargs = {}
        request = self.request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request

    def test_case_stage_bad_data(self):
        form = PleaOnlineForms("case", "plea_form_step", self.session)
        response = form.load(self.request_context)
        response = form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 4)

    def test_case_stage_good_data(self):
        form = PleaOnlineForms("case", "plea_form_step", self.session)
        response = form.load(self.request_context)
        response = form.save({"date_of_hearing_0": "01",
                              "date_of_hearing_1": "01",
                              "date_of_hearing_2": "2015",
                              "time_of_hearing": "09:15",
                              "urn_0": "00",
                              "urn_1": "AA",
                              "urn_2": "0000000",
                              "urn_3": "00",
                              "number_of_charges": "1"},
                             self.request_context)

        self.assertEqual(response.status_code, 302)

    def test_your_details_stage_bad_data(self):
        form = PleaOnlineForms("your_details", "plea_form_step", self.session)
        response = form.load(self.request_context)
        response = form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 3)

    def test_your_details_stage_good_data(self):
        form = PleaOnlineForms("your_details", "plea_form_step", self.session)
        response = form.load(self.request_context)
        response = form.save({"name": "Test man",
                              "contact_number": "012345678",
                              "email": "test.man@example.org"},
                             self.request_context)

        self.assertEqual(response.status_code, 302)

    def test_plea_stage_bad_data_single_charge(self):
        self.session.update(self.plea_stage_pre_data_1_charge)
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        mgmt_data = {"form-TOTAL_FORMS": "1",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}
        mgmt_data.update({"form-0-guilty": "",
                          "form-0-mitigations": ""})

        # no form data, just the management stuff
        form.save(mgmt_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors[0]), 1)

    def test_plea_stage_good_data_single_charge(self):
        self.session.update(self.plea_stage_pre_data_1_charge)
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        mgmt_data = {"form-TOTAL_FORMS": "1",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1"})

        response = form.save(mgmt_data, self.request_context)

        self.assertEqual(response.status_code, 302)

    def test_plea_stage_bad_data_multiple_charges(self):
        self.session.update(self.plea_stage_pre_data_1_charge)
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1"})

        response = form.save(mgmt_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors[0]), 0)
        self.assertEqual(len(form.current_stage.forms[0].errors[1]), 1)

    def test_plea_stage_good_data_multiple_charges(self):
        self.session.update(self.plea_stage_pre_data_1_charge)
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1",
                          "form-1-guilty": "guilty",
                          "form-1-mitigations": "lorem ipsum 1"})

        response = form.save(mgmt_data, self.request_context)

        self.assertEqual(response.status_code, 302)

    def test_review_stage_loads(self):
        pass

    def test_complete_stage_loads(self):
        pass

    def test_reviewsenderror_stage_loads(self):
        pass

    def test_email_error_redirects_to_reviewsenderror_stage(self):
        pass

    def test_successful_completion_single_charge(self):
        fake_session = {}
        fake_request = self.get_request_mock("/plea/case")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms("case", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"date_of_hearing_0": "01",
                              "date_of_hearing_1": "01",
                              "date_of_hearing_2": "2015",
                              "time_of_hearing": "09:15",
                              "urn_0": "00",
                              "urn_1": "AA",
                              "urn_2": "0000000",
                              "urn_3": "00",
                              "number_of_charges": "1"},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("your_details", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"name": "Charlie Brown",
                              "contact_number": "07802639892",
                              "email": "test@example.org"},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("plea", "plea_form_step", fake_session)
        response = form.load(request_context)

        mgmt_data = {"form-TOTAL_FORMS": "1",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1"})

        response = form.save(mgmt_data, request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("review", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"understand": "True"},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("complete", "plea_form_step", fake_session)
        response = form.load(request_context)

        self.assertEqual(fake_session["case"]["date_of_hearing"], datetime.date(2015, 1, 1))
        self.assertEqual(fake_session["case"]["time_of_hearing"], datetime.time(9, 15))
        self.assertEqual(fake_session["case"]["urn"], "00/AA/0000000/00")
        self.assertEqual(fake_session["case"]["number_of_charges"], 1)
        self.assertEqual(fake_session["your_details"]["name"], "Charlie Brown")
        self.assertEqual(fake_session["your_details"]["contact_number"], "07802639892")
        self.assertEqual(fake_session["your_details"]["email"], "test@example.org")
        self.assertEqual(fake_session["plea"]["PleaForms"][0]["guilty"], "guilty")
        self.assertEqual(fake_session["plea"]["PleaForms"][0]["mitigations"], "lorem ipsum 1")
        self.assertEqual(fake_session["review"]["understand"], True)

    def test_successful_completion_multiple_charges(self):
        fake_session = {}
        fake_request = self.get_request_mock("/plea/case/")

        request_context = RequestContext(fake_request)

        form = PleaOnlineForms("case", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"date_of_hearing_0": "01",
                              "date_of_hearing_1": "01",
                              "date_of_hearing_2": "2015",
                              "time_of_hearing": "09:15",
                              "urn_0": "00",
                              "urn_1": "AA",
                              "urn_2": "0000000",
                              "urn_3": "00",
                              "number_of_charges": "2"},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("your_details", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"name": "Charlie Brown",
                              "contact_number": "07802639892",
                              "email": "test@example.org"},
                             request_context)

        form = PleaOnlineForms("plea", "plea_form_step", fake_session)
        response = form.load(request_context)

        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1",
                          "form-1-guilty": "guilty",
                          "form-1-mitigations": "lorem ipsum 2"})

        response = form.save(mgmt_data, request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("review", "plea_form_step", fake_session)
        response = form.load(request_context)
        response = form.save({"understand": "True"},
                             request_context)

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("complete", "plea_form_step", fake_session)
        response = form.load(request_context)

        self.assertEqual(fake_session["case"]["date_of_hearing"], datetime.date(2015, 1, 1))
        self.assertEqual(fake_session["case"]["time_of_hearing"], datetime.time(9, 15))
        self.assertEqual(fake_session["case"]["urn"], "00/AA/0000000/00")
        self.assertEqual(fake_session["case"]["number_of_charges"], 2)
        self.assertEqual(fake_session["your_details"]["name"], "Charlie Brown")
        self.assertEqual(fake_session["your_details"]["contact_number"], "07802639892")
        self.assertEqual(fake_session["your_details"]["email"], "test@example.org")
        self.assertEqual(fake_session["plea"]["PleaForms"][0]["guilty"], "guilty")
        self.assertEqual(fake_session["plea"]["PleaForms"][0]["mitigations"], "lorem ipsum 1")
        self.assertEqual(fake_session["plea"]["PleaForms"][1]["guilty"], "guilty")
        self.assertEqual(fake_session["plea"]["PleaForms"][1]["mitigations"], "lorem ipsum 2")
        self.assertEqual(fake_session["review"]["understand"], True)
