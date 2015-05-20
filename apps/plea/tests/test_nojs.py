from django.test import TestCase
from django.test.client import RequestFactory
from mock import Mock
from django.template.context import RequestContext

from ..views import PleaOnlineForms

class TestNoJS(TestCase):

    def setUp(self):
        self.session = {"case": {"complete": True, "number_of_charges": 1},
                        "your_details": {"complete": True}}
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

    def test_nojs_plea_stage_bad_data_no_trigger_summary(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        form.save({"nojs": "guilty",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_nojs_plea_stage_good_data_trigger_summary(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        form.save({"nojs": "guilty",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1",
                   "form-0-guilty": "guilty"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<<NOJSTRIGGERSUMMARY>>")

    def test_nojs_plea_stage_last_step_summary_and_errors(self):
        form = PleaOnlineForms("plea", "plea_form_step", self.session)

        form.save({"nojs": "nojs_last_step",
                   "form-TOTAL_FORMS": "1",
                   "form-INITIAL_FORMS": "0",
                   "form-MAX_NUM_FORMS": "1",
                   "form-0-guilty": "not_guilty"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<<NOJSTRIGGERSUMMARY>>")
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_nojs_plea_stage_change_link_no_summary(self):
        self.session.update({"plea": {"nojs": "nojs_last_step",
                                      "form-0-guilty": "guilty"}})

        fake_request = self.get_request_mock("/plea/plea/?reset")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms("case", "plea_form_step", self.session)

        form.load(request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<<NOJSTRIGGERSUMMARY>>")