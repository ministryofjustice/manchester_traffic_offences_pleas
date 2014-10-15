import datetime
from mock import Mock, MagicMock, patch
import socket

from django.test import TestCase
from django.test.client import RequestFactory
from django.template.context import RequestContext

from ..models import CourtEmailPlea
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
                                                      "number_of_charges": 1},
                                             "your_details": {"name": "Charlie Brown",
                                                              "contact_number": "012345678",
                                                              "email": "charliebrown@example.org"}}

        self.plea_stage_pre_data_3_charges = {"case": {"date_of_hearing": "2015-01-01",
                                                       "urn_0": "00",
                                                       "urn_1": "AA",
                                                       "urn_2": "0000000",
                                                       "urn_3": "00",
                                                       "number_of_charges": 3},
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
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 4)

    def test_case_stage_urn_already_submitted(self):

        email_audit = CourtEmailPlea()
        email_audit.urn = "00/aa/0000000/00"
        email_audit.hearing_date = datetime.datetime.now()
        email_audit.status = "sent"
        email_audit.save()

        form = PleaOnlineForms("case", "plea_form_step", self.session)
        form.load(self.request_context)
        form.save({"date_of_hearing_0": "01",
                   "date_of_hearing_1": "01",
                   "date_of_hearing_2": "2015",
                   "time_of_hearing": "09:15",
                   "urn_0": "00",
                   "urn_1": "AA",
                   "urn_2": "0000000",
                   "urn_3": "00",
                   "number_of_charges": 1},
                  self.request_context)

        response = form.render()

        self.assertEquals(form.current_stage.forms[0].errors.keys()[0], 'urn')
        self.assertEquals(response.status_code, 200)

    def test_case_stage_good_data(self):
        form = PleaOnlineForms("case", "plea_form_step", self.session)
        form.load(self.request_context)
        form.save({"date_of_hearing_0": "01",
                   "date_of_hearing_1": "01",
                   "date_of_hearing_2": "2015",
                   "time_of_hearing": "09:15",
                   "urn_0": "00",
                   "urn_1": "AA",
                   "urn_2": "0000000",
                   "urn_3": "00",
                   "number_of_charges": 1},
                  self.request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

    def test_your_details_stage_bad_data(self):
        form = PleaOnlineForms("your_details", "plea_form_step", self.session)
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 3)

    def test_your_details_stage_good_data(self):
        form = PleaOnlineForms("your_details", "plea_form_step", self.session)
        form.load(self.request_context)
        form.save({"name": "Test man",
                   "contact_number": "012345678",
                   "email": "test.man@example.org"},
                  self.request_context)
        response = form.render()
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

        form.save(mgmt_data, self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

    def test_plea_stage_missing_data_multiple_charges(self):
        self.session.update(self.plea_stage_pre_data_3_charges)
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        mgmt_data = {"form-TOTAL_FORMS": "3",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1"})

        form.save(mgmt_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors[0]), 0)
        self.assertEqual(len(form.current_stage.forms[0].errors[1]), 1)
        self.assertEqual(len(form.current_stage.forms[0].errors[2]), 1)

    def test_plea_stage_bad_data_multiple_charges(self):
        self.session.update(self.plea_stage_pre_data_1_charge)
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "2",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1"})

        form.save(mgmt_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].forms), 1)

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

        form.save(mgmt_data, self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

    def _get_your_money_stage(self):
        test_data = {
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "urn": "00/AA/0000000/00",
                "number_of_charges": 1
            },
            "your_details": {
                "complete": True
            },
            "plea": {
                "complete": True
            }
        }

        form = PleaOnlineForms("your_money", "plea_form_step", test_data)

        form.load(self.request_context)

        return form

    def test_your_money_stage_loads(self):

        form = self._get_your_money_stage()

        response = form.render()

        self.assertEquals(response.status_code, 200)

    def test_your_money_employment_type_required(self):

        form = self._get_your_money_stage()

        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 1)

    def test_your_money_employed_option_with_required_fields_missing(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Employed"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 5)

    def test_your_money_employed_option_with_valid_data(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Employed",
            "employer_name": "test",
            "employer_address": "test",
            "employer_phone": "test",
            "take_home_pay_period": "Fortnightly",
            "take_home_pay_amount": "1000"
        }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.forms[0].is_valid())

    def test_your_money_self_employed_option_with_required_fields_missing(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Self employed"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 3)

    def test_your_money_self_employed_option_with_valid_data(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Self employed",
            "your_job": "Build trains",
            "self_employed_pay_period": "Fortnightly",
            "self_employed_pay_amount": "1000"
        }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.forms[0].is_valid())

    def test_your_money_benefits_option_with_required_fields_missing(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Receiving benefits"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 2)

    def test_your_money_benefits_option_with_valid_data(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Receiving benefits",
            "benefits_period": "Fortnightly",
            "benefits_amount": "1000"
        }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.forms[0].is_valid())

    def test_your_money_other_option_with_required_fields_missing(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Other"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.forms[0].errors), 1)

    def test_your_money_other_option_with_valid_data(self):

        form = self._get_your_money_stage()

        test_data = {
            "you_are": "Other",
            "other_info": "woo woo woo"
            }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.forms[0].is_valid())

    def test_review_stage_loads(self):
        test_data = {
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "urn": "00/AA/0000000/00",
                "number_of_charges": 1
            },
            "your_details": {
                "complete": True
            },
            "plea": {
                "complete": True
            },
            "your_money":  {
                "complete": True
            }
        }

        form = PleaOnlineForms("review", "plea_form_step", test_data)

        form.load(self.request_context)
        response = form.render()

        self.assertTemplateUsed(response, "plea/review.html")
        self.assertIn("00/AA/0000000/00", response.content)

    def test_complete_stage_loads(self):

        test_data = {
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "urn": "00/AA/0000000/00",
                "number_of_charges": 1
            },
            "your_details": {
                "complete": True
            },
            "plea": {
                "complete": True,
                "PleaForms": [
                    {
                        "guilty": "guilty",
                        "mitigations": "something"
                    },
                    {
                        "guilty": "guilty",
                        "mitigations": "something"
                    },
                    {
                        "guilty": "guilty",
                        "mitigations": "something"
                    }
                ]
            },
            "your_money":  {
                "complete": True
            },
            "review": {
                "complete": True
            }
        }

        form = PleaOnlineForms("complete", "plea_form_step", test_data)
        fake_request = self.get_request_mock("/plea/complete")
        request_context = RequestContext(fake_request)

        form.load(request_context)
        response = form.render()

        self.assertIn(test_data["case"]["urn"], response.content)

    @patch("apps.plea.email.TemplateAttachmentEmail.send")
    @patch("apps.govuk_utils.forms.messages.add_message")
    def test_email_error_adds_message(self, add_message, send):
        send.side_effect = socket.error("Email failed to send, socket error")

        fake_session = {"case": {}, "your_details": {}, "plea": {"PleaForms": [{}]}, "review": {}}
        fake_session["case"]["date_of_hearing"] = datetime.date(2015, 1, 1)
        fake_session["case"]["time_of_hearing"] = datetime.time(9, 15)
        fake_session["case"]["urn"] = "00/AA/0000000/00"
        fake_session["case"]["number_of_charges"] = 1
        fake_session["your_details"]["name"] = "Charlie Brown"
        fake_session["your_details"]["contact_number"] = "07802639892"
        fake_session["your_details"]["email"] = "test@example.org"
        fake_session['your_details']["national_insurance_number"] = "test NI number"
        fake_session['your_details']["driving_licence_number"] = "test driving number"
        fake_session['your_details']["registration_number"] = "test registration number"
        fake_session["plea"]["PleaForms"][0]["guilty"] = "guilty"
        fake_session["plea"]["PleaForms"][0]["mitigations"] = "lorem ipsum 1"

        form = PleaOnlineForms("review", "plea_form_step", fake_session)
        form.load(self.request_context)
        form.save({"understand": True}, self.request_context)
        form.process_messages({})
        self.assertEqual(add_message.call_count, 1)
        self.assertEqual(add_message.call_args[0][0], {})
        self.assertEqual(add_message.call_args[0][1], 40)
        self.assertTrue(isinstance(add_message.call_args[0][2], basestring))

    def test_successful_completion_single_charge(self):
        fake_session = {}
        fake_request = self.get_request_mock("/plea/case")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms("case", "plea_form_step", fake_session)
        form.load(request_context)
        form.save({"date_of_hearing_0": "01",
                   "date_of_hearing_1": "01",
                   "date_of_hearing_2": "2015",
                   "time_of_hearing": "09:15",
                   "urn_0": "00",
                   "urn_1": "AA",
                   "urn_2": "0000000",
                   "urn_3": "00",
                   "number_of_charges": 1},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("your_details", "plea_form_step", fake_session)
        form.load(request_context)
        form.save({"name": "Charlie Brown",
                   "contact_number": "07802639892",
                   "email": "test@example.org"},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("plea", "plea_form_step", fake_session)
        form.load(request_context)

        mgmt_data = {"form-TOTAL_FORMS": "1",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1"})

        form.save(mgmt_data, request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("review", "plea_form_step", fake_session)
        form.load(request_context)
        form.save({"understand": "True"},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("complete", "plea_form_step", fake_session)
        form.load(request_context)

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
        form.load(request_context)
        form.save({"date_of_hearing_0": "01",
                   "date_of_hearing_1": "01",
                   "date_of_hearing_2": "2015",
                   "time_of_hearing": "09:15",
                   "urn_0": "00",
                   "urn_1": "AA",
                   "urn_2": "0000000",
                   "urn_3": "00",
                   "number_of_charges": 2},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("your_details", "plea_form_step", fake_session)
        form.load(request_context)
        form.save({"name": "Charlie Brown",
                   "contact_number": "07802639892",
                   "email": "test@example.org"},
                  request_context)

        form = PleaOnlineForms("plea", "plea_form_step", fake_session)
        form.load(request_context)

        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}

        mgmt_data.update({"form-0-guilty": "guilty",
                          "form-0-mitigations": "lorem ipsum 1",
                          "form-1-guilty": "guilty",
                          "form-1-mitigations": "lorem ipsum 2"})

        form.save(mgmt_data, request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("review", "plea_form_step", fake_session)
        form.load(request_context)
        form.save({"understand": "True"},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms("complete", "plea_form_step", fake_session)
        form.load(request_context)

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