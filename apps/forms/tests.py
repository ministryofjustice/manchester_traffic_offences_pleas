from mock import Mock, patch

from django import forms
from django.contrib import messages
from django.forms.formsets import formset_factory
from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import translation
from .forms import to_bool, BaseStageForm
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


class TestForm3(forms.Form):
    skip_stage_5 = forms.BooleanField()


class TestForm4(BaseStageForm):
    dependencies = {
        "field7": {
            "field": "field6",
            "value": "True"
        }
    }

    field6 = forms.TypedChoiceField(coerce=to_bool,
                                    choices=((True, "Yes"),
                                             (False, "No")))
    field7 = forms.DecimalField(required=True, min_value=10)


class TestForm5(BaseStageForm):
    """This form tests when a dependency is triggered by multiple optional values
    """
    CHOICES = (
        ('a', 'option a'), ('b', 'option b'),
        ('c', 'option c'), ('d', 'option d')
    )
    dependencies = {
        "field7": {
            "field": "field6",
            "value": "a|b|c"
        },
        "field8": {
            "field": "field6",
            "value": "a|b"
        }
    }

    field6 = forms.ChoiceField(
        choices=CHOICES,
        required=True)
    field7 = forms.DecimalField(required=True, min_value=10)
    field8 = forms.DecimalField(required=True, min_value=10)


class Intro(FormStage):
    name = "intro"
    template = "test/intro.html"
    form_class = None


class Stage2(FormStage):
    name = "stage_2"
    template = "test/stage.html"
    form_class = TestForm1


class Stage3(FormStage):
    name = "stage_3"
    form_class = TestForm2
    template = "test/stage.html"
    dependencies = ["stage_2"]

    def load_forms(self, data=None, initial=False):
        count = self.all_data["stage_2"].get("field2", 1)

        TestForm2Factory = formset_factory(TestForm2, extra=count)
        if initial:
            initial_factory_data = self.all_data[self.name].get("Factory", [])
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


class Stage4(FormStage):
    name = "stage_4"
    storage_key = "stage_4"
    form_class = TestForm3
    template = "test/stage.html"
    dependencies = ["stage_2", "stage_3"]

    def save(self, form_data, next_step=None):
        clean_data = super(Stage4, self).save(form_data, next_step)

        if "skip_stage_5" in clean_data and clean_data["skip_stage_5"] is True:
            self.set_next_step("review", skip=["stage_5"])
        else:
            self.set_next_step("stage_5")

        return clean_data


class Stage45(FormStage):
    name = "stage_45"
    storage_key = "stage_4"
    form_class = TestForm1
    template = "test/stage.html"
    dependencies = ["stage_4", ]


class Stage5(FormStage):
    name = "stage_5"
    form_class = TestForm1
    template = "test/stage.html"
    dependencies = ["stage_2", "stage_3", "stage_4"]


class Stage6(FormStage):
    name = "stage_6"
    form_class = TestForm4
    template = "test/stage.html"
    dependencies = ["stage_2", "stage_3", "stage_4", "stage_5"]


class AlternateStage6(FormStage):
    """This alternate version of stage 6 tests for alternate dependencies"""
    name = "alternate_stage_6"
    form_class = TestForm5
    template = "test/stage.html"
    dependencies = ["stage_2", "stage_3", "stage_4", "stage_5"]


class Review(FormStage):
    name = "review"
    template = "test/review.html"
    form_class = None
    dependencies = ["stage_2", "stage_3", "stage_4", "stage_5", "stage_6"]


class TestCaseBase(TestCase):
    def get_request_mock(self, url="/", url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request


class MultiStageFormTest(MultiStageForm, TestCaseBase):
    url_name = "msf-url"
    stage_classes = [Intro, Stage2, Stage3, Stage4, Stage45, Stage5, Stage6, AlternateStage6, Review]


class TestMultiStageForm(TestCase):
    def setUp(self):
        self.request_context = Mock()
        self.request_context.request = RequestFactory().get('/dummy')

    @patch("apps.forms.stages.reverse", reverse)
    def test_404_raised_if_no_stage(self):
        with self.assertRaises(Http404):
            MultiStageFormTest({}, "Rabbits")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_intro_loads(self):
        msf = MultiStageFormTest({}, "intro")
        msf.load(self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertContains(response, "<h1>Test intro page</h1>")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage2_loads(self):
        msf = MultiStageFormTest({}, "stage_2")
        msf.load(self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertContains(response, "id_field1")
        self.assertContains(response, "id_field2")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage2_saves(self):
        msf = MultiStageFormTest({}, "stage_2")
        msf.load(self.request_context)
        msf.save({"field1": "Joe",
                  "field2": 10},
                 self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertEqual(msf.all_data["stage_2"]["field1"], "Joe")
        self.assertEqual(msf.all_data["stage_2"]["field2"], 10)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1],
                         "/path/to/msf-url/stage_3")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage3_unmet_dependencies(self):
        session_data = {}
        msf = MultiStageFormTest(session_data, "stage_3")
        response = msf.load(self.request_context)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/path/to/msf-url/intro")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage3_loads(self):
        session_data = {"stage_2": {"complete": True,
                                    "field2": 2}}
        msf = MultiStageFormTest(session_data, "stage_3")
        msf.load(self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertContains(response, "id_form-0-field3")
        self.assertContains(response, "id_form-0-field4")
        self.assertContains(response, "id_form-1-field3")
        self.assertContains(response, "id_form-1-field4")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage3_saves(self):
        session_data = {"stage_2": {"complete": True}}
        msf = MultiStageFormTest(session_data, "stage_3")
        msf.all_data["field2"] = 2
        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}
        form_data = {"form-0-field3": "Jim Smith",
                     "form-0-field4": "jim.smith@example.org",
                     "form-1-field3": "Jill Smith",
                     "form-1-field4": "jill.smith@example.org"}
        form_data.update(mgmt_data)
        msf.save(form_data, self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertEqual(msf.all_data["stage_3"]["Factory"][0]["field3"], "Jim Smith")
        self.assertEqual(msf.all_data["stage_3"]["Factory"][0]["field4"], "jim.smith@example.org")
        self.assertEqual(msf.all_data["stage_3"]["Factory"][1]["field3"], "Jill Smith")
        self.assertEqual(msf.all_data["stage_3"]["Factory"][1]["field4"], "jill.smith@example.org")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], "/path/to/msf-url/stage_4")

    @patch("apps.forms.stages.reverse", reverse)
    @patch("apps.forms.stages.messages.add_message")
    def test_form_stage3_messages(self, add_msg):
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
        msf.save(form_data, self.request_context)
        msf.process_messages({})

        add_msg.assert_called_once_with({}, 25, "This is a test message", extra_tags=None)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage45_loads_specified_key(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True,
                                    "field1": "Stage 45 field 1 data"}}
        msf = MultiStageFormTest(session_data, "stage_45")
        msf.load(self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertContains(response, 'value="Stage 45 field 1 data"')

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage45_saves_to_specified_key(self):
        msf = MultiStageFormTest({}, "stage_45")
        msf.load(self.request_context)
        msf.save({"field1": "Stage 4",
                  "field2": 4},
                 self.request_context)

        self.assertEqual(msf.all_data["stage_4"]["field1"], "Stage 4")
        self.assertEqual(msf.all_data["stage_4"]["field2"], 4)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage4_unmet_dependencies(self):
        session_data = {}
        msf = MultiStageFormTest(session_data, "stage_4")
        response = msf.load(self.request_context)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/path/to/msf-url/intro")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage4_loads(self):
        session_data = {"stage_2": {"complete": True,
                                    "field2": 1},
                        "stage_3": {"complete": True,
                                    "Factory": [{"field3": "Jim Smith",
                                                 "field4": "jim.smith@example.org"}]}}
        msf = MultiStageFormTest(session_data, "stage_4")
        msf.load(self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "id_skip_stage_5")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage5_marked_skipped(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True}}
        msf = MultiStageFormTest(session_data, "stage_4")
        msf.load(self.request_context)
        msf.save({"skip_stage_5": True}, self.request_context)

        self.assertIn("skipped", msf.all_data["stage_5"])
        self.assertEqual(msf.all_data["stage_5"]["skipped"], True)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage5_marked_not_skipped(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True}}
        msf = MultiStageFormTest(session_data, "stage_4")
        msf.load(self.request_context)
        msf.save({"skip_stage_5": False}, self.request_context)

        self.assertNotIn("skipped", msf.all_data["stage_5"])

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage6_field7_required(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "stage_6")
        msf.load(self.request_context)
        msf.save({"field6": True}, self.request_context)

        self.assertIn("field7", msf.current_stage.form.errors)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage6_field7_validates(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "stage_6")
        msf.load(self.request_context)
        msf.save({"field6": True, "field7": 0}, self.request_context)

        self.assertIn("field7", msf.current_stage.form.errors)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage6_field7_not_required(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "stage_6")
        msf.load(self.request_context)
        msf.save({"field6": False}, self.request_context)

        self.assertNotIn("field7", msf.current_stage.form.errors)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage6_field7_suppress_validation_errors(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "stage_6")
        msf.load(self.request_context)
        msf.save({"field6": False, "field7": 0}, self.request_context)

        self.assertNotIn("field7", msf.current_stage.form.errors)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_alternatestage6_fields7and8_required(self):
        """When field 6 has a value of b, both fields 7 and 8 should be required"""
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "alternate_stage_6")
        msf.load(self.request_context)
        msf.save({"field6": u'b'}, self.request_context)

        self.assertIn("field7", msf.current_stage.form.errors)
        self.assertIn("field8", msf.current_stage.form.errors)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_alternatestage6_fields7_required(self):
        """When field 6 has a value of c, only field 7 should be required"""
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "alternate_stage_6")
        msf.load(self.request_context)
        msf.save({"field6": u'c'}, self.request_context)

        self.assertIn("field7", msf.current_stage.form.errors )
        self.assertNotIn("field8", msf.current_stage.form.errors)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_alternatestage6_fields7and8_not_required(self):
        """When field 6 has a value of d, neither fields 7 nor 8 should be required"""
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "alternate_stage_6")
        msf.load(self.request_context)
        msf.save({"field6": u'd'}, self.request_context)

        self.assertNotIn("field7", msf.current_stage.form.errors)
        self.assertNotIn("field8", msf.current_stage.form.errors)

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_review_unmet_dependencies(self):
        msf = MultiStageFormTest({}, "review")
        response = msf.load(self.request_context)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/path/to/msf-url/intro")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_review_loads_skipped_dependencies(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True, "skipped": True}}
        msf = MultiStageFormTest(session_data, "review")
        msf.load(self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Review</h1>")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_review_loads(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True}}
        msf = MultiStageFormTest(session_data, "review")
        msf.load(self.request_context)
        response = msf.render(msf.get_request_mock())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Review</h1>")

    @patch("apps.forms.stages.reverse", reverse)
    def test_form_stage5_unskipped(self):
        session_data = {"stage_2": {"complete": True},
                        "stage_3": {"complete": True},
                        "stage_4": {"complete": True},
                        "stage_5": {"complete": True, "skipped": True}}
        msf = MultiStageFormTest(session_data, "stage_4")
        msf.load(self.request_context)
        msf.save({"skip_stage_5": False}, self.request_context)

        self.assertNotIn("skipped", session_data["stage_5"])

    @patch("apps.forms.stages.reverse", reverse)
    def test_save_doesnt_blank_storage_dict_and_nothing_is_added(self):
        fake_storage = {"extra": {"field0": "Not on the form"}}
        msf = MultiStageFormTest(fake_storage, "intro")
        msf.load(self.request_context)
        msf.save({}, self.request_context)

        self.assertTrue(fake_storage["extra"]["field0"], "Not on the form")
        self.assertEqual(len(fake_storage["extra"]), 1)

    @patch("apps.forms.stages.reverse", reverse)
    def test_save_data_persists_between_stages(self):
        fake_storage = {}
        msf = MultiStageFormTest(fake_storage, "stage_2")
        msf.load(self.request_context)

        msf.save({"field1": "Joe",
                  "field2": 2},
                 self.request_context)

        msf = MultiStageFormTest(fake_storage, "stage_3")
        mgmt_data = {"form-TOTAL_FORMS": "2",
                     "form-INITIAL_FORMS": "0",
                     "form-MAX_NUM_FORMS": "1000"}
        form_data = {"form-0-field3": "Jim Smith",
                     "form-0-field4": "jim.smith@example.org",
                     "form-1-field3": "Jill Smith",
                     "form-1-field4": "jill.smith@example.org"}
        form_data.update(mgmt_data)
        msf.save(form_data, self.request_context)

        self.assertEqual(fake_storage["stage_2"]["field1"], "Joe")
        self.assertEqual(fake_storage["stage_2"]["field2"], 2)
        self.assertEqual(fake_storage["stage_3"]["Factory"][0]["field3"], "Jim Smith")
        self.assertEqual(fake_storage["stage_3"]["Factory"][0]["field4"], "jim.smith@example.org")
        self.assertEqual(fake_storage["stage_3"]["Factory"][1]["field3"], "Jill Smith")
        self.assertEqual(fake_storage["stage_3"]["Factory"][1]["field4"], "jill.smith@example.org")

    @patch("apps.forms.stages.reverse", reverse)
    def test_stage_standard_single_form_validation(self):
        msf = MultiStageFormTest({}, "stage_2")
        msf.load(self.request_context)
        msf.save({"field1": "",
                  "field2": "This is not an integer"},
                 self.request_context)
        response = msf.render(msf.get_request_mock())

        # check it doesn't redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a whole number")
        self.assertContains(response, "This field is required")
