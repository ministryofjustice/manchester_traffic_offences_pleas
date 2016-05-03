from django.core.exceptions import NON_FIELD_ERRORS
from django.http.response import HttpResponseRedirect

from ..views import PleaOnlineForms
from ..models import Case, Court
from ..standardisers import standardise_name

from test_plea_form import TestMultiPleaFormBase


class TestPleaFormIssues(TestMultiPleaFormBase):
    def setUp(self):
        self.session = {}
        self.request_context = {}

    def test_used_urn_in_session(self):
        case = Case.objects.create(urn="06AA000000000",
                                   extra_data={"FirstName1": "Frank",
                                               "Surname": "Marsh"},
                                   name="frank marsh",
                                   sent=True)
        case.save()

        self.session = {"notice_type": {"complete": True,
                                        "sjp": False},
                        "case": {"complete": True,
                                 "date_of_hearing": "2015-01-01",
                                 "urn": "06AA000000000",
                                 "number_of_charges": 1,
                                 "plea_made_by": "Defendant"},
                        "your_details": {"first_name": "Frank",
                                         "last_name": "Marsh"}}

        save_data = {"date_of_hearing": "2015-01-01",
                     "urn": "06/AA/0000000/00",
                     "number_of_charges": 1,
                     "plea_made_by": "Defendant"}

        form = PleaOnlineForms(self.session, "case")
        form.save(save_data, self.request_context)

        result = form.render()
        self.assertIsInstance(result, HttpResponseRedirect)


class TestDuplicateCaseIssues(TestMultiPleaFormBase):

    def setUp(self):
        Court.objects.create(region_code="51",
                             enabled=True)

    def create_person_case(self, urn, first_name, last_name):
        return Case.objects.create(urn=urn,
                                   name=standardise_name(first_name, last_name),
                                   extra_data={"FirstName1": first_name,
                                               "Surname": last_name},
                                   sent=True)

    def create_company_case(self, urn, first_name, last_name, org_name):
        return Case.objects.create(urn=urn,
                                   extra_data={"OrganisationName": org_name,
                                               "FirstName1": first_name,
                                               "Surname": last_name},
                                   sent=True)

    def get_session_data(self, urn, type):
        return {"notice_type": {"complete": True,
                                "sjp": False},
                "case": {"complete": True,
                         "date_of_hearing": "2016-01-01",
                         "urn": urn,
                         "number_of_charges": 1,
                         "plea_made_by": type}}

    def get_person_details_save_data(self, first_name, last_name):
        return {"first_name": first_name,
                "last_name": last_name,
                "correct_address": "True",
                "updated_address": "",
                "contact_number": "0236578493",
                "date_of_birth_0": "01",
                "date_of_birth_1": "01",
                "date_of_birth_2": "1970",
                "have_ni_number": "False",
                "have_driving_licence_number": "False"}

    def get_company_details_save_data(self, company_name, first_name, last_name):
        return {"company_name": company_name,
                "correct_address": "True",
                "first_name": first_name,
                "last_name": last_name,
                "position_in_company": "Director",
                "contact_number": "0236578493"}

    def test_dup_person_same_name(self):
        self.create_person_case("51aa0000015", "Frank", "Marsh")
        session = self.get_session_data("51aa0000015", "Defendant")
        form = self.get_person_details_save_data("Frank", "Marsh")

        stages = PleaOnlineForms(session, "your_details")
        stages.save(form, {})

        self.assertEqual(len(stages.current_stage.form.errors[NON_FIELD_ERRORS]), 1)

    def test_dup_person_different_names(self):
        self.create_person_case("51aa0000015", "Frank", "Marsh")
        session = self.get_session_data("51aa0000015", "Defendant")
        form = self.get_person_details_save_data("Franky", "Marshington III")

        stages = PleaOnlineForms(session, "your_details")
        stages.save(form, {})

        self.assertEqual(stages.current_stage.form.errors, {})

    def test_dup_company(self):
        self.create_company_case("51bb0000015", "Frank", "Marsh", "Frank Marsh inc.")
        session = self.get_session_data("51bb0000015", "Company representative")
        form = self.get_company_details_save_data("Frank Marsh inc.", "Frank", "Marsh")

        stages = PleaOnlineForms(session, "company_details")
        stages.save(form, {})

        self.assertEqual(len(stages.current_stage.form.errors[NON_FIELD_ERRORS]), 1)

    def test_dup_company_different_names(self):
        self.create_company_case("51bb0000015", "Frank", "Marsh", "Frank Marsh inc.")
        session = self.get_session_data("51bb0000015", "Company representative")
        form = self.get_company_details_save_data("Frank Marsh inc.", "Frankie", "Marshington III")

        stages = PleaOnlineForms(session, "company_details")
        stages.save(form, {})

        self.assertEqual(len(stages.current_stage.form.errors[NON_FIELD_ERRORS]), 1)

    def test_person_then_company(self):
        self.create_person_case("51aa0000015", "Frank", "Marsh")

        session = self.get_session_data("51aa0000015", "Company representative")
        form = self.get_company_details_save_data("Frank Marsh inc.", "Frank", "Marsh")

        stages = PleaOnlineForms(session, "company_details")
        stages.save(form, {})

        self.assertEqual(len(stages.current_stage.form.errors[NON_FIELD_ERRORS]), 1)

    def test_company_then_person_different_name(self):
        self.create_company_case("51aa0000015", "Frank", "Marsh", "Frank Marsh inc.")

        session = self.get_session_data("51aa0000015", "Defendant")
        form = self.get_person_details_save_data("Franky", "Marshington III")

        stages = PleaOnlineForms(session, "your_details")
        stages.save(form, {})

        self.assertEqual(len(stages.current_stage.form.errors[NON_FIELD_ERRORS]), 1)

    def test_company_then_person_same_name(self):
        self.create_company_case("51aa0000015", "Frank", "Marsh", "Frank Marsh inc.")

        session = self.get_session_data("51aa0000015", "Defendant")
        form = self.get_person_details_save_data("Frank", "Marsh")

        stages = PleaOnlineForms(session, "your_details")
        stages.save(form, {})

        self.assertEqual(len(stages.current_stage.form.errors[NON_FIELD_ERRORS]), 1)
