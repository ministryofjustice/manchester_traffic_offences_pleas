from mock import patch

from django import forms
from django.contrib import messages
from django.forms.formsets import formset_factory
from django.http import Http404
from django.test import TestCase
from .stages import MultiStageForm, FormStage


def reverse(url_name, args=None):
    return "/path/to/" + url_name + "/" + args[0]


def add_message(request, importance, message):
    pass


class TestForm1(forms.Form):
    field1 = forms.CharField()
    field2 = forms.IntegerField()


class TestForm2(forms.Form):
    field3 = forms.CharField()
    field4 = forms.EmailField()


class Intro(FormStage):
    name = "intro"
    template = "test/intro.html"
    form_class = None


class Stage2(FormStage):
    name = "stage_2"
    template = "test/stage2.html"
    form_class = TestForm1


class Stage3(FormStage):
    name = "stage_3"
    form_class= TestForm2
    template = "test/stage3.html"

    def load_forms(self, data=None, initial=False):
        count = self.all_data["stage_2"].get("field2", 1)

        TestForm2Factory = formset_factory(TestForm2, extra=count)
        if initial:
            initial_factory_data = self.all_data[self.name].get("Factory", [])
            initial_form_data = self.all_data[self.name]
            self.form = TestForm2Factory(initial=initial_factory_data)
        else:
            self.form = TestForm2Factory(data)

    def save_forms(self):
        form_data = {}

        if hasattr(self.form, "management_form"):
            form_data["Factory"] = self.form.cleaned_data
        else:
            form_data.update(self.form.cleaned_data)

        self.add_message(messages.SUCCESS, "This is a test message")

        return form_data


class Review(FormStage):
    name = "review"
    template = "test/review.html"
    form_class = None


class MultiStageFormTest(MultiStageForm):
    url_name = "msf-url"
    stage_classes = [Intro, Stage2, Stage3, Review]


class TestMultiStageForm(TestCase):
    @patch("apps.forms.stages.reverse", reverse)
    def test_404_raised_if_no_stage(self):
        with self.assertRaises(Http404):
            MultiStageFormTest({}, "Rabbits")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_intro_loads(self):
        request_context = {}
        msf = MultiStageFormTest({}, "intro")
        msf.load(request_context)
        response = msf.render()
        self.assertContains(response, "<h1>Test intro page</h1>")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage2_loads(self):
        request_context = {}
        msf = MultiStageFormTest({}, "stage_2")
        msf.load(request_context)
        response = msf.render()
        self.assertContains(response, "id_field1")
        self.assertContains(response, "id_field2")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage2_saves(self):
        request_context = {}
        msf = MultiStageFormTest({}, "stage_2")
        msf.load(request_context)
        msf.save({"field1": "Joe",
                             "field2": 10},
                            request_context)
        response = msf.render()

        self.assertEqual(msf.all_data["stage_2"]["field1"], "Joe")
        self.assertEqual(msf.all_data["stage_2"]["field2"], 10)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1],
                         "/path/to/msf-url/stage_3")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage3_loads(self):
        request_context = {}
        msf = MultiStageFormTest({}, "stage_3")
        msf.all_data["stage_2"]["field2"] = 2
        msf.load(request_context)
        response = msf.render()
        self.assertContains(response, "id_form-0-field3")
        self.assertContains(response, "id_form-0-field4")
        self.assertContains(response, "id_form-1-field3")
        self.assertContains(response, "id_form-1-field4")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage3_saves(self):
        request_context = {}
        msf = MultiStageFormTest({}, "stage_3")
        msf.all_data["field2"] = 2
        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}
        form_data = {"form-0-field3": "Jim Smith",
                     "form-0-field4": "jim.smith@example.org",
                     "form-1-field3": "Jill Smith",
                     "form-1-field4": "jill.smith@example.org"}
        form_data.update(mgmt_data)
        msf.save(form_data, request_context)

    @patch("apps.forms.stages.reverse", reverse)
    @patch("apps.forms.stages.messages.add_message")
    def test_form_stage3_messages(self, add_message):
        request_context = {}
        msf = MultiStageFormTest({}, "stage_3")
        msf.all_data["field2"] = 2
        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}
        form_data = {"form-0-field3": "Jim Smith",
                     "form-0-field4": "jim.smith@example.org",
                     "form-1-field3": "Jill Smith",
                     "form-1-field4": "jill.smith@example.org"}
        form_data.update(mgmt_data)
        msf.save(form_data, request_context)
        msf.process_messages({})
        add_message.assert_called_once_with({}, 25, "This is a test message", extra_tags=None)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_review_loads(self):
        request_context = {}
        msf = MultiStageFormTest({}, "review")
        msf.load(request_context)
        response = msf.render()
        self.assertContains(response, "<h1>Review</h1>")

    @patch("apps.forms.stages.reverse", reverse)
    def test_save_doesnt_blank_storage_dict_and_nothing_is_added(self):
        request_context = {}
        fake_storage = {"extra": {"field0": "Not on the form"}}
        msf = MultiStageFormTest(fake_storage, "intro")
        msf.load(request_context)
        msf.save({}, request_context)
        self.assertTrue(fake_storage["extra"]["field0"], "Not on the form")
        self.assertEqual(len(fake_storage["extra"]), 1)

    @patch("apps.forms.stages.reverse", reverse)
    def test_save_data_persists_between_stages(self):
        request_context = {}
        fake_storage = {}
        msf = MultiStageFormTest(fake_storage, "stage_2")
        msf.load(request_context)

        response = msf.save({"field1": "Joe",
                             "field2": 2},
                            request_context)

        msf = MultiStageFormTest(fake_storage, "stage_3")
        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}
        form_data = {"form-0-field3": "Jim Smith",
                     "form-0-field4": "jim.smith@example.org",
                     "form-1-field3": "Jill Smith",
                     "form-1-field4": "jill.smith@example.org"}
        form_data.update(mgmt_data)
        response = msf.save(form_data, request_context)

        self.assertEqual(fake_storage["stage_2"]["field1"], "Joe")
        self.assertEqual(fake_storage["stage_2"]["field2"], 2)
        self.assertEqual(fake_storage["stage_3"]["Factory"][0]["field3"], "Jim Smith")
        self.assertEqual(fake_storage["stage_3"]["Factory"][0]["field4"], "jim.smith@example.org")
        self.assertEqual(fake_storage["stage_3"]["Factory"][1]["field3"], "Jill Smith")
        self.assertEqual(fake_storage["stage_3"]["Factory"][1]["field4"], "jill.smith@example.org")

    @patch("apps.forms.stages.reverse", reverse)
    def test_stage_standard_single_form_validation(self):
        request_context = {}
        msf = MultiStageFormTest({}, "stage_2")
        msf.load(request_context)
        msf.save({"field1": "",
                  "field2": "This is not an integer"},
                  request_context)
        response = msf.render()

        # check it doesn't redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a whole number")
        self.assertContains(response, "This field is required")
