from django.test import TestCase
from django.test.client import RequestFactory
from mock import Mock
from django.template.context import RequestContext

from ..views import PleaOnlineForms

class TestNoJS(TestCase):

    def setUp(self):
        self.plea_session = {"case": {"complete": True, 
                                      "number_of_charges": 1,
                                      "plea_made_by": "Defendant"},
                             "your_details": {"complete": True}}

        self.company_finances_session = {"case": {"complete": True,
                                                  "plea_made_by": "Company representative"},
                                         "company_details": {"complete": True},
                                         "plea": {"complete": True,
                                                  "PleaForms": [{"guilty": "guilty"}]}}

        self.request_context = {}

    def get_request_mock(self, url, url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request

    def test_split_form_plea_stage_bad_data_no_trigger_summary(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.plea_session)

        form.save({"split_form": "guilty",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_split_form_plea_stage_good_data_trigger_summary(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.plea_session)

        form.save({"split_form": "guilty",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1",
                   "form-0-guilty": "guilty"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_split_form_plea_stage_last_step_summary_and_errors(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.plea_session)

        form.save({"split_form": "split_form_last_step",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1",
                   "form-0-guilty": "not_guilty"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<<NOJSTRIGGERSUMMARY>>")
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_split_form_plea_stage_change_link_no_summary(self):
        self.plea_session.update({"plea": {"split_form": "split_form_last_step",
                                      "form-0-guilty": "guilty"}})

        fake_request = self.get_request_mock("/plea/plea/?reset")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms("plea", "plea_form_step", self.plea_session)

        form.load(request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_split_form_plea_stage_submits(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.plea_session)

        form.save({"split_form": "split_form_last_step",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1",
                   "form-0-guilty": "not_guilty",
                   "form-0-not_guilty_extra": "Lorem ipsum",
                   "form-0-interpreter_needed": True,
                   "form-0-interpreter_language": "French"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/plea/review/')


    def test_split_form_plea_stage_errors(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.plea_session)

        form.save({"split_form": "split_form_last_step",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1",
                   "form-0-guilty": "not_guilty",
                   "form-0-interpreter_needed": True},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 1)


    def test_split_form_company_finances_stage_bad_data_no_trigger_summary(self):
        form = PleaOnlineForms("company_finances", "plea_form_step", self.company_finances_session)

        form.save({"split_form": "trading_period"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_split_form_company_finances_stage_good_data_trigger_summary(self):
        form = PleaOnlineForms("company_finances", "plea_form_step", self.company_finances_session)

        form.save({"split_form": "trading_period",
                   "trading_period": True},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_split_form_company_finances_stage_last_step_summary_and_errors(self):
        form = PleaOnlineForms("company_finances", "plea_form_step", self.company_finances_session)

        form.save({"split_form": "split_form_last_step",
                   "trading_period": True},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<<NOJSTRIGGERSUMMARY>>")
        self.assertEqual(len(form.current_stage.form.errors), 3)

    def test_split_form_company_finances_stage_change_link_no_summary(self):
        self.company_finances_session.update({"company_finances": {"split_form": "split_form_last_step",
                                                                   "trading_period": True}})

        fake_request = self.get_request_mock("/plea/company_finances/?reset")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms("company_finances", "plea_form_step", self.company_finances_session)

        form.load(request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_split_form_company_finances_stage_submits(self):
        form = PleaOnlineForms("company_finances", "plea_form_step", self.company_finances_session)

        form.save({"split_form": "split_form_last_step",
                   "trading_period": True,
                   "number_of_employees": "10",
                   "gross_turnover": "19000",
                   "net_turnover": "12000"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/plea/review/')
