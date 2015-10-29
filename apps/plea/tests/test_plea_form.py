import datetime
from mock import Mock, patch

from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.template.context import RequestContext

from ..models import Case, Court
from ..views import PleaOnlineForms


class TestMultiPleaFormBase(TestCase):

    def get_request_mock(self, url, url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs
        return request


class TestMultiPleaForms(TestMultiPleaFormBase):
    def setUp(self):

        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="test@test.com",
            submission_email=True,
            plp_email="test@test.com",
            enabled=True,
            test_mode=False)

        self.session = {}
        self.request_context = {}

        self.plea_stage_pre_data_1_charge = {"notice_type": {"sjp": False},
                                             "case": {"date_of_hearing": "2015-01-01",
                                                      "urn": "06/AA/0000000/00",
                                                      "number_of_charges": 1,
                                                      "plea_made_by": "Defendant"},
                                             "your_details": {"first_name": "Charlie",
                                                              "last_name": "Brown",
                                                              "contact_number": "012345678"}}

        self.plea_stage_pre_data_3_charges = {"notice_type": {"sjp": False},
                                              "case": {"date_of_hearing": "2015-01-01",
                                                       "urn": "06/AA/0000000/00",
                                                       "number_of_charges": 3,
                                                       "plea_made_by": "Defendant"},
                                              "your_details": {"first_name": "Charlie",
                                                               "last_name": "Brown",
                                                               "contact_number": "012345678"}}

        self.test_session_data = {
            "notice_type": {
                "complete": True,
                "sjp": False
            },
            "case": {
                "complete": True,
                "date_of_hearing": "2015-01-01",
                "urn": "06/AA/0000000/00",
                "number_of_charges": 3,
                "plea_made_by": "Defendant"
            },
            "your_details": {
                "complete": True,
                "first_name": "Charlie",
                "last_name": "Brown",
                "contact_number": "07802639892"
            },
            "plea": {
                "data": [
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something",
                        "complete": True,
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something",
                        "complete": True,
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something",
                        "complete": True,
                    }
                ]
            },
            "your_finances": {
                "complete": True,
                "you_are": "Employed",
                "employer_name": "test",
                "employer_address": "test",
                "employer_phone": "test",
                "take_home_pay_period": "Fortnightly",
                "take_home_pay_amount": "1000",
                "employer_hardship": True
            },
            "hardship": {
                "complete": True
            },
            "household_expenses": {
                "complete": True
            },
            "other_expenses": {
                "complete": True
            },
            "your_expenses": {
                "total_household_expenses": 999
            },
            "review": {
                "receive_email_updates": True,
                "email": "test@test.com",
                "understand": True,
                "complete": True
            }
        }

    def test_notice_type_stage_missing_data(self):
        form = PleaOnlineForms(self.session, "notice_type")
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_notice_type_stage_good_data(self):
        form = PleaOnlineForms(self.session, "notice_type")

        form.load(self.request_context)
        form.save({"sjp": True},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/case/")

    def test_case_stage_bad_data(self):
        form = PleaOnlineForms(self.session, "case")
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 4)

    def test_case_stage_urn_already_submitted(self):

        fake_request = self.get_request_mock("/plea/case/")
        request_context = RequestContext(fake_request)

        case = Case()
        case.urn = "06/AA/0000000/00"
        case.sent = True
        case.save()

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        form = PleaOnlineForms(self.session, "case")
        form.load(request_context)

        form.save({"date_of_hearing_0": str(hearing_date.day),
                   "date_of_hearing_1": str(hearing_date.month),
                   "date_of_hearing_2": str(hearing_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 1,
                   "plea_made_by": "Defendant"},
                  request_context)

        response = form.render()

        court_obj = Court.objects.get(region_code="06")

        self.assertContains(
            response,
            "<br />".join(court_obj.court_address.split("\n")))

        self.assertContains(response, court_obj.court_email)

        self.assertEqual(form.current_stage.form.errors.keys()[0], "urn")
        self.assertEqual(response.status_code, 200)

    def test_case_stage_good_data(self):
        form = PleaOnlineForms(self.session, "case")

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        form.load(self.request_context)
        form.save({"date_of_hearing_0": str(hearing_date.day),
                   "date_of_hearing_1": str(hearing_date.month),
                   "date_of_hearing_2": str(hearing_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 1,
                   "plea_made_by": "Defendant"},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

    def test_case_stage_redirects_to_company_stage(self):
        form = PleaOnlineForms(self.session, "case")

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        form.load(self.request_context)
        form.save({"date_of_hearing_0": str(hearing_date.day),
                   "date_of_hearing_1": str(hearing_date.month),
                   "date_of_hearing_2": str(hearing_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 1,
                   "plea_made_by": "Company representative"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/company_details/")

    def test_case_stage_redirects_to_your_finances_stage(self):
        form = PleaOnlineForms(self.session, "case")

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        form.load(self.request_context)
        form.save({"date_of_hearing_0": str(hearing_date.day),
                   "date_of_hearing_1": str(hearing_date.month),
                   "date_of_hearing_2": str(hearing_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 1,
                   "plea_made_by": "Defendant"},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/your_details/")

    def test_your_details_stage_bad_data(self):
        form = PleaOnlineForms(self.session, "your_details")
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 7)

    def test_your_details_stage_good_data(self):
        form = PleaOnlineForms(self.session, "your_details")
        form.load(self.request_context)
        form.save({"first_name": "Test",
                   "last_name": "Man",
                   "contact_number": "012345678",
                   "correct_address": True,
                   "date_of_birth_0": "12",
                   "date_of_birth_1": "03",
                   "date_of_birth_2": "1980",
                   "have_ni_number": False,
                   "have_driving_licence_number": False},
                  self.request_context)

        response = form.render()
        self.assertEqual(response.status_code, 302)

    def test_your_details_stage_optional_data_required(self):
        form = PleaOnlineForms(self.session, "your_details")
        form.load(self.request_context)

        form_data = {"first_name": "Test",
                     "last_name": "Man",
                     "contact_number": "012345678",
                     "correct_address": False,
                     "date_of_birth_0": "12",
                     "date_of_birth_1": "03",
                     "date_of_birth_2": "1980",
                     "have_ni_number": True,
                     "have_driving_licence_number": True}

        form.save(form_data, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertIn("updated_address", form.current_stage.form.errors)
        self.assertIn("ni_number", form.current_stage.form.errors)
        self.assertIn("driving_licence_number", form.current_stage.form.errors)
        self.assertEqual(len(form.current_stage.form.errors), 3)

        form_data.update({"updated_address": "Test address",
                          "ni_number": "QQ123456C",
                          "driving_licence_number": "TESTE12345"})
        form.save(form_data, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)

    def test_company_details_stage_updated_address_required(self):
        form = PleaOnlineForms(self.session, "company_details")
        form.load(self.request_context)

        form_data = {"company_name": "Test Company",
                     "correct_address": False,
                     "first_name": "John",
                     "last_name": "Smith",
                     "position_in_company": "Director",
                     "contact_number": "07000000000"}

        form.save(form_data, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertIn("updated_address", form.current_stage.form.errors)
        self.assertEqual(len(form.current_stage.form.errors), 1)

        form_data.update({"updated_address": "Test address"})
        form.save(form_data, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)

    def test_plea_single_charge_missing_data(self):
        self.session.update(self.plea_stage_pre_data_1_charge)

        form = PleaOnlineForms(self.session, "plea", 1)

        form.load(self.request_context)
        form.save({},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_plea_SJP_single_charge_guilty_missing_data(self):
        self.session.update(self.plea_stage_pre_data_1_charge)
        self.session["notice_type"]["sjp"] = True

        form = PleaOnlineForms(self.session, "plea", 1)

        form.load(self.request_context)
        form.save({"guilty": "guilty"},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_plea_SJP_single_charge_guilty_missing_extra_data(self):
        self.session.update(self.plea_stage_pre_data_1_charge)
        self.session["notice_type"]["sjp"] = True

        form = PleaOnlineForms(self.session, "plea", 1)

        form.load(self.request_context)
        form.save({"guilty": "guilty",
                   "come_to_court": True},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_plea_single_charge_not_guilty_missing_data(self):
        self.session.update(self.plea_stage_pre_data_1_charge)

        form = PleaOnlineForms(self.session, "plea", 1)

        form.load(self.request_context)
        form.save({"guilty": "not_guilty"},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 4)

    def test_plea_single_charge_not_guilty_missing_extra_data(self):
        self.session.update(self.plea_stage_pre_data_1_charge)

        form = PleaOnlineForms(self.session, "plea", 1)

        form.load(self.request_context)
        form.save({"guilty": "not_guilty",
                   "not_guilty_extra": "lorem",
                   "interpreter_needed": True,
                   "disagree_with_evidence": True,
                   "witness_needed": True},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 4)

    def test_plea_single_charge_not_guilty_missing_witness_language(self):
        self.session.update(self.plea_stage_pre_data_1_charge)

        form = PleaOnlineForms(self.session, "plea", 1)

        form.load(self.request_context)
        form.save({"guilty": "not_guilty",
                   "not_guilty_extra": "lorem",
                   "interpreter_needed": True,
                   "interpreter_language": "French",
                   "disagree_with_evidence": True,
                   "disagree_with_evidence_details": "lorem",
                   "witness_needed": True,
                   "witness_details": "lorem"},
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_plea_stage_redirects_when_valid(self):
        self.session.update(self.plea_stage_pre_data_1_charge)

        # plea 1
        form = PleaOnlineForms(self.session, "plea", 1)

        plea_1 = {"guilty": "guilty",
                  "guilty_extra": "lorem ipsum 1"}

        form.load(self.request_context)
        form.save(plea_1,
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)


        # plea 2
        form = PleaOnlineForms(self.session, "plea", 2)
        plea_1 = {"guilty": "not_guilty",
                  "not_guilty_extra": "lorem ipsum 1",
                  "interpreter_needed": False,
                  "disagree_with_evidence": False,
                  "witness_needed": False}

        form.load(self.request_context)
        form.save(plea_1,
                  self.request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/your_finances/")

    def test_plea_stage_redirects_to_company_finances(self):

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        fake_request = self.get_request_mock("/plea/plea/")
        request_context = RequestContext(fake_request)

        test_data = {
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Company representative"
            },
            "your_details": {
                "complete": True
            },
            "your_finances": {
                "complete": True
            },
            "plea": {

            }
        }

        form = PleaOnlineForms(test_data, "plea", 1)
        form.load(request_context)

        plea_data = {"guilty": "guilty",
                     "guilty_extra": "lorem ipsum 1"}

        form.save(plea_data, request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/company_finances/")

    def test_plea_stage_skips_company_finances_when_not_guilty(self):
        hearing_date = datetime.date.today()+datetime.timedelta(30)

        fake_request = self.get_request_mock("/plea/plea/")
        request_context = RequestContext(fake_request)

        test_data = {
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Company representative"
            },
            "your_details": {
                "complete": True
            },
            "your_finances": {
                "complete": True
            },
            "plea": {
            }
        }

        form = PleaOnlineForms(test_data, "plea", 1)
        form.load(request_context)

        plea_data = {"guilty": "not_guilty",
                     "not_guilty_extra": "lorem ipsum 1",
                     "interpreter_needed": False,
                     "disagree_with_evidence": False,
                     "witness_needed": False}

        form.save(plea_data, request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/review/")

    def _get_your_finances_stage(self):
        hearing_date = datetime.date.today()+datetime.timedelta(30)

        test_data = {
            "notice_type": {
                "complete": True,
                "sjp": False
            },
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Defendant"
            },
            "your_details": {
                "complete": True
            },
            "plea": {
                "complete": True
            }
        }

        form = PleaOnlineForms(test_data, "your_finances")

        form.load(self.request_context)

        return form

    def test_your_finances_stage_loads(self):

        form = self._get_your_finances_stage()

        response = form.render()

        self.assertEqual(response.status_code, 200)

    def test_your_finances_employment_type_required(self):

        form = self._get_your_finances_stage()

        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_your_finances_employed_option_with_required_fields_missing(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Employed"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 3)

    def test_your_finances_employed_option_with_valid_data(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Employed",
            "employed_take_home_pay_period": "Fortnightly",
            "employed_take_home_pay_amount": "1000",
            "employed_hardship": True
        }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.form.is_valid())

    def test_your_finances_self_employed_option_with_required_fields_missing(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Self-employed"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 3)

    def test_your_finances_self_employed_option_with_valid_data(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Self-employed",
            "self_employed_pay_period": "Fortnightly",
            "self_employed_pay_amount": "1000",
            "self_employed_hardship": False
        }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.form.is_valid())

    def test_your_finances_benefits_option_with_required_fields_missing(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Receiving benefits"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 5)

    def test_your_finances_benefits_option_with_valid_data(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Receiving benefits",
            "benefits_details": "Some data about my benefits",
            "benefits_dependents": True,
            "benefits_period": "Fortnightly",
            "benefits_amount": "1000",
            "receiving_benefits_hardship": False
        }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.form.is_valid())

    def test_your_finances_other_option_with_required_fields_missing(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Other"
        }

        form.save(test_data, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 3)

    def test_your_finances_other_option_with_valid_data(self):

        form = self._get_your_finances_stage()

        test_data = {
            "you_are": "Other",
            "other_details": "woo woo woo",
            "other_pay_amount": "100",
            "other_hardship": False
        }

        form.save(test_data, self.request_context)

        self.assertTrue(form.current_stage.form.is_valid())

    @patch("apps.forms.stages.messages.add_message")
    def test_review_stage_session_timeout_redirects_to_case(self, add_message):
        # no test data to simulate a timed out session
        test_data = {
            "case": {}
        }

        form = PleaOnlineForms(test_data, "review")

        form.save({"understand": True}, self.request_context)
        form.process_messages({})
        response = form.render()

        self.assertEqual(add_message.call_count, 1)
        self.assertEqual(add_message.call_args[0][0], {})
        self.assertEqual(add_message.call_args[0][1], 40)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/case/")

    def test_review_stage_has_company_details_block(self):
        hearing_date = datetime.date.today()+datetime.timedelta(30)

        test_data = {
            "notice_type": {
                "complete": True,
                "sjp": False
            },
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Company representative"
            },
            "your_details": {
                "complete": True,
                "skipped": True
            },
            "company_details": {
                "company_name": "TEST COMPANY",
                "updated_address": "TEST ADDRESS",
                "first_name": "TEST",
                "last_name": "NAME",
                "position_in_company": "a director",
                "contact_number": "0800 TEST",
                "complete": True
            },
            "plea": {
                "data": [
                    {
                        "guilty": "not_guilty",
                        "not_guilty_extra": "",
                        "complete": True
                    }
                ],
            },
            "your_finances":  {
                "complete": True,
                "skipped": True
            },
            "company_finances": {
                "skipped": True,
                "complete": True
            }
        }

        form = PleaOnlineForms(test_data, "review")

        form.load(self.request_context)
        response = form.render()

        self.assertContains(response, "<<SHOWCOMPANYDETAILS>>")
        self.assertContains(response, test_data["company_details"]["company_name"])
        self.assertContains(response, test_data["company_details"]["first_name"])
        self.assertContains(response, test_data["company_details"]["last_name"])
        self.assertContains(response, test_data["company_details"]["position_in_company"])
        self.assertContains(response, test_data["company_details"]["contact_number"])

        self.assertNotContains(response, "<<SHOWYOURDETAILS>>")
        self.assertNotContains(response, "<<SHOWCOMPANYFINANCES>>")
        self.assertNotContains(response, "<<SHOWINGEXPENSES>>")

    def test_review_stage_has_company_finances_block(self):
        hearing_date = datetime.date.today()+datetime.timedelta(30)

        test_data = {
            "notice_type": {
                "complete": True,
                "sjp": False
            },
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Company representative"
            },
            "your_details": {
                "complete": True,
                "skipped": True
            },
            "company_details": {
                "company_name": "TEST COMPANY",
                "updated_address": "TEST ADDRESS",
                "first_name": "TEST",
                "last_name": "NAME",
                "position_in_company": "a director",
                "contact_number": "0800 TEST",
                "complete": True
            },
            "plea": {
                "data": [
                    {
                        "guilty": "guilty",
                        "guilty_extra": "",
                        "complete": True
                    }
                ],
            },
            "your_finances":  {
                "complete": True,
                "skipped": True
            },
            "company_finances": {
                "complete": True
            }
        }

        form = PleaOnlineForms(test_data, "review")

        form.load(self.request_context)
        response = form.render()

        self.assertContains(response, "<<SHOWCOMPANYDETAILS>>")
        self.assertContains(response, test_data["company_details"]["company_name"])
        self.assertContains(response, test_data["company_details"]["first_name"])
        self.assertContains(response, test_data["company_details"]["last_name"])
        self.assertContains(response, test_data["company_details"]["position_in_company"])
        self.assertContains(response, test_data["company_details"]["contact_number"])

        self.assertContains(response, "<<SHOWCOMPANYFINANCES>>")
        self.assertNotContains(response, "<<SHOWYOURDETAILS>>")
        self.assertNotContains(response, "<<SHOWINGEXPENSES>>")

    def test_review_stage_loads(self):
        hearing_date = datetime.date.today()+datetime.timedelta(30)

        test_data = {
            "notice_type": {
                "complete": True
            },
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Defendant"
            },
            "your_details": {
                "complete": True
            },
            "plea": {
                "complete": True
            },
            "your_finances":  {
                "complete": True
            },
            "company_details": {
                "complete": True
            },
            "company_finances": {
                "complete": True
            }
        }

        form = PleaOnlineForms(test_data, "review")

        form.load(self.request_context)

        with self.assertTemplateUsed("review.html"):
            response = form.render()
            self.assertIn("06/AA/0000000/00", response.content)

    def test_review_stage_missing_data(self):
        form = PleaOnlineForms(self.session, "review")
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 2)

    def test_review_stage_missing_email(self):
        form = PleaOnlineForms(self.session, "review")
        form.load(self.request_context)
        form.save({"receive_email_updates": True,
                   "understand": True},
                  self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_review_stage_good_data(self):
        form = PleaOnlineForms(self.session, "review")
        form.load(self.request_context)
        form.save({"receive_email_updates": True,
                   "email": "test@test.com",
                   "understand": True},
                  self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)

    def test_complete_stage_loads(self):
        hearing_date = datetime.date.today()+datetime.timedelta(30)

        test_data = {
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Defendant"
            },
            "your_details": {
                "complete": True
            },
            "plea": {
                "complete": True,
                "data": [
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something"
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something"
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something"
                    }
                ]
            },
            "your_finances":  {
                "complete": True
            },
            "review": {
                "complete": True
            }
        }

        form = PleaOnlineForms(test_data, "complete")
        fake_request = self.get_request_mock("/plea/complete")
        request_context = RequestContext(fake_request)

        form.load(request_context)
        response = form.render()

        court_obj = Court.objects.get(region_code="06")

        self.assertContains(
            response,
            "<br />".join(court_obj.court_address.split("\n")))

        self.assertIn(test_data["case"]["urn"], response.content)

    def test_successful_completion_single_charge(self):
        fake_session = {}
        fake_request = self.get_request_mock("/plea/notice_type/")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(fake_session, "notice_type")
        form.load(request_context)
        form.save({"sjp": False},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        form = PleaOnlineForms(fake_session, "case")
        form.load(request_context)
        form.save({"date_of_hearing_0": str(hearing_date.day),
                   "date_of_hearing_1": str(hearing_date.month),
                   "date_of_hearing_2": str(hearing_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 1,
                   "plea_made_by": "Defendant"},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms(fake_session, "your_details")
        form.load(request_context)
        form.save({"first_name": "Charlie",
                   "last_name": "Brown",
                   "contact_number": "07802639892",
                   "correct_address": True,
                   "date_of_birth_0": "12",
                   "date_of_birth_1": "03",
                   "date_of_birth_2": "1980",
                   "have_ni_number": False,
                   "have_driving_licence_number": False},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms(fake_session, "plea", 1)
        form.load(request_context)

        plea_data = {"guilty": "guilty",
                     "guilty_extra": "lorem ipsum 1"}

        form.save(plea_data, request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms(fake_session, "review")
        form.load(request_context)
        form.save({"receive_email_updates": True,
                   "email": "test@test.com",
                   "understand": True},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms(fake_session, "complete")
        form.load(request_context)

        self.assertEqual(fake_session["case"]["date_of_hearing"], hearing_date)
        self.assertEqual(fake_session["case"]["urn"], "06/AA/0000000/00")
        self.assertEqual(fake_session["case"]["number_of_charges"], 1)
        self.assertEqual(fake_session["your_details"]["first_name"], "Charlie")
        self.assertEqual(fake_session["your_details"]["last_name"], "Brown")
        self.assertEqual(fake_session["your_details"]["contact_number"], "07802639892")
        self.assertEqual(fake_session["plea"]["data"][0]["guilty"], "guilty")
        self.assertEqual(fake_session["plea"]["data"][0]["guilty_extra"], "lorem ipsum 1")
        self.assertEqual(fake_session["review"]["understand"], True)

    def test_successful_completion_multiple_charges(self):
        fake_session = {}
        fake_request = self.get_request_mock("/plea/notice_type/")

        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(fake_session, "notice_type")
        form.load(request_context)
        form.save({"sjp": False},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        form = PleaOnlineForms(fake_session, "case")
        form.load(request_context)
        form.save({"date_of_hearing_0": str(hearing_date.day),
                   "date_of_hearing_1": str(hearing_date.month),
                   "date_of_hearing_2": str(hearing_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 2,
                   "plea_made_by": "Defendant"},
                  request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms(fake_session, "your_details")
        form.load(request_context)
        form.save({"first_name": "Charlie",
                   "last_name": "Brown",
                   "contact_number": "07802639892",
                   "correct_address": True,
                   "date_of_birth_0": "12",
                   "date_of_birth_1": "03",
                   "date_of_birth_2": "1980",
                   "have_ni_number": False,
                   "have_driving_licence_number": False},
                  request_context)

        # plea 1
        form = PleaOnlineForms(fake_session, "plea", 1)
        form.load(request_context)

        plea_data = {"guilty": "guilty",
                     "guilty_extra": "lorem ipsum 1"}

        form.save(plea_data, request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

        # plea 1
        form = PleaOnlineForms(fake_session, "plea", 2)
        form.load(request_context)

        plea_data = {"guilty": "guilty",
                     "guilty_extra": "lorem ipsum 2"}

        form.save(plea_data, request_context)
        response = form.render()

        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms(fake_session, "review")
        form.load(request_context)
        form.save({"receive_email_updates": True,
                   "email": "test@test.com",
                   "understand": True},
                  request_context)
        response = form.render()
        self.assertEqual(response.status_code, 302)

        form = PleaOnlineForms(fake_session, "complete")
        form.load(request_context)

        self.assertEqual(fake_session["case"]["date_of_hearing"], hearing_date)
        self.assertEqual(fake_session["case"]["urn"], "06/AA/0000000/00")
        self.assertEqual(fake_session["case"]["number_of_charges"], 2)
        self.assertEqual(fake_session["case"]["plea_made_by"], "Defendant")
        self.assertEqual(fake_session["your_details"]["first_name"], "Charlie")
        self.assertEqual(fake_session["your_details"]["last_name"], "Brown")
        self.assertEqual(fake_session["your_details"]["contact_number"], "07802639892")
        self.assertEqual(fake_session["plea"]["data"][0]["guilty"], "guilty")
        self.assertEqual(fake_session["plea"]["data"][0]["guilty_extra"], "lorem ipsum 1")
        self.assertEqual(fake_session["plea"]["data"][1]["guilty"], "guilty")
        self.assertEqual(fake_session["plea"]["data"][1]["guilty_extra"], "lorem ipsum 2")
        self.assertEqual(fake_session["review"]["understand"], True)

    def test_guilty_pleas_complete_page_content(self):

        fake_request = self.get_request_mock("/plea/complete")
        request_context = RequestContext(fake_request)

        stage_data = self.test_session_data

        form = PleaOnlineForms(stage_data, "complete")
        form.load(request_context)

        response = form.render()

        self.assertContains(response, "<<GUILTY>>")

    def test_mixed_pleas_complete_page_content(self):

        fake_request = self.get_request_mock("/plea/complete")
        request_context = RequestContext(fake_request)

        stage_data = self.test_session_data

        stage_data["plea"]["data"][0]["guilty"] = "not_guilty"

        form = PleaOnlineForms(stage_data, "complete")
        form.load(request_context)

        response = form.render()

        self.assertContains(response, "<<MIXED>>")

    def test_not_guilty_pleas_complete_page_content(self):

        fake_request = self.get_request_mock("/plea/complete")
        request_context = RequestContext(fake_request)

        stage_data = self.test_session_data

        stage_data["plea"]["data"] = [
            {
                "mitigation": "asdf",
                "guilty": "not_guilty"
            },
            {
                "mitigation": "asdf",
                "guilty": "not_guilty"
            },
            {
                "mitigation": "asdf",
                "guilty": "not_guilty"
            }
        ]

        form = PleaOnlineForms(stage_data, "complete")
        form.load(request_context)

        response = form.render()

        self.assertContains(response, "<<NOTGUILTY>>")


    def test_non_sjp_contact_deadline_is_date_of_hearing(self):
        fake_session = {
            "notice_type": {
                "sjp": False
            }
        }

        hearing_date = datetime.date.today() + datetime.timedelta(30)

        fake_request = self.get_request_mock("/plea/case")
        request_context = RequestContext(fake_request)
        form = PleaOnlineForms(fake_session, "case")
        form.save({"date_of_hearing_0": str(hearing_date.day),
                   "date_of_hearing_1": str(hearing_date.month),
                   "date_of_hearing_2": str(hearing_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 2,
                   "plea_made_by": "Defendant"},
                  request_context)

        self.assertEquals(fake_session["case"]["contact_deadline"], hearing_date)

    def test_sjp_contact_deadline_is_28_days_after_posting_date(self):
        fake_session = {
            "notice_type": {
                "sjp": True
            }
        }

        posting_date = datetime.date.today() - datetime.timedelta(10)
        contact_deadline = posting_date + datetime.timedelta(28)

        fake_request = self.get_request_mock("/plea/case")
        request_context = RequestContext(fake_request)
        form = PleaOnlineForms(fake_session, "case")
        form.save({"posting_date_0": str(posting_date.day),
                   "posting_date_1": str(posting_date.month),
                   "posting_date_2": str(posting_date.year),
                   "urn": "06/AA/0000000/00",
                   "number_of_charges": 2,
                   "plea_made_by": "Defendant"},
                  request_context)

        self.assertEquals(fake_session["case"]["contact_deadline"], contact_deadline)

    def test_case_stage_urn_in_session(self):

        urn = "06/AA/0000000/00"

        case = Case()
        case.urn = urn
        case.sent = True
        case.save()

        self.session["case"] = dict(urn=urn)

        form = PleaOnlineForms(self.session, "case")
        form.load(self.request_context)
        form.save({}, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("urn_already_used"))

    def test_urn_not_success_is_not_blocked(self):

        urn = "06/AA/0000000/00"

        case = Case()
        case.urn = urn
        case.status = "network_error"
        case.save()

        self.session["case"] = dict(urn=urn)

        form = PleaOnlineForms(self.session, "case")
        form.load(self.request_context)
        form.save({}, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)

    def test_your_finances_employed_hardship_redirects_to_hardship(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Employed",
            "employed_take_home_pay_period": "Fortnightly",
            "employed_take_home_pay_amount": "1000",
            "employed_hardship": True
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/hardship/")

    def test_hardship_redirects_to_household_expenses(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/hardship")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "hardship")

        form.load(request_context)

        test_data = {
            "hardship_details": "ra ra ra"
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/household_expenses/")

    def test_household_expenses_redirects_to_other_expenses(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/household_expenses")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "household_expenses")

        form.load(request_context)

        test_data = {
            "household_accommodation": "0",
            "household_utility_bills": "0",
            "household_insurance": "100",
            "household_council_tax": "50",
            "other_bill_payers": True
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/other_expenses/")

    def test_other_expenses_redirects_to_review_page(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/other_expenses")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "other_expenses")

        form.load(request_context)

        test_data = {
            "other_tv_subscription": "0",
            "other_travel_expenses": "20",
            "other_telephone": "40",
            "other_loan_repayments": "60",
            "other_court_payments": "30",
            "other_child_maintenance": "50"
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/plea/review/")

    def test_your_finances_employed_no_hardship_redirects_to_review(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Employed",
            "employed_take_home_pay_period": "Fortnightly",
            "employed_take_home_pay_amount": "1000",
            "employed_hardship": False
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/review/")

    def test_your_finances_self_employed_hardship_redirects_to_hardship(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Self-employed",
            "self_employed_pay_period": "Fortnightly",
            "self_employed_pay_amount": "1000",
            "self_employed_hardship": True
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/hardship/")

    def test_your_finances_self_employed_no_hardship_redirects_to_review(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Self-employed",
            "self_employed_pay_period": "Fortnightly",
            "self_employed_pay_amount": "1000",
            "self_employed_hardship": False
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/review/")

    def test_your_finances_benefits_hardship_redirects_to_hardship(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Receiving benefits",
            "benefits_details": "Some data about my benefits",
            "benefits_dependents": True,
            "benefits_period": "Fortnightly",
            "benefits_amount": "1000",
            "receiving_benefits_hardship": True
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/hardship/")

    def test_your_finances_benefits_no_hardship_redirects_to_review(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Receiving benefits",
            "benefits_details": "Some data about my benefits",
            "benefits_dependents": True,
            "benefits_period": "Fortnightly",
            "benefits_amount": "1000",
            "receiving_benefits_hardship": False
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/review/")

    def test_your_finances_other_hardship_redirects_to_hardship(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Other",
            "other_details": "woo woo woo",
            "other_pay_amount": "100",
            "other_hardship": True
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/hardship/")

    def test_your_finances_other_no_hardship_redirects_to_review(self):

        session_data = self.test_session_data
        fake_request = self.get_request_mock("/plea/your_expenses")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Other",
            "other_details": "woo woo woo",
            "other_pay_amount": "100",
            "other_hardship": False
        }

        form.save(test_data, request_context)

        response = form.render()

        self.assertEqual(response.url, "/plea/review/")

    def test_hardship_calculations_on_review_page(self):

        session_data = self.test_session_data
        session_data["company_details"] = {"complete": True}
        session_data["your_finances"]["hardship"] = True

        fake_request = self.get_request_mock("/plea/other_expenses")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "other_expenses")

        form.load(request_context)

        test_data = {
            "other_tv_subscription": "111",
            "other_travel_expenses": "111",
            "other_telephone": "111",
            "other_loan_repayments": "111",
            "other_court_payments": "111",
            "other_child_maintenance": "111"
        }

        form.save(test_data, request_context)

        form = PleaOnlineForms(session_data, "review")

        form.load(request_context)

        response = form.render()

        self.assertContains(response, "999.00")
        self.assertContains(response, "666.00")
        self.assertContains(response, "1,665.00")

    def test_hardship_on_review(self):

        session_data = self.test_session_data
        session_data["company_details"] = {"complete": True}
        session_data["company_finances"] = {"complete": True}

        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Other",
            "other_details": "woo woo woo",
            "other_pay_amount": "100",
            "other_hardship": True
        }

        form.save(test_data, request_context)

        form = PleaOnlineForms(session_data, "review")

        form.load(request_context)

        response = form.render()

        self.assertContains(response, "<<SHOWINGEXPENSES>>")

    def test_no_hardship_review(self):

        session_data = self.test_session_data
        session_data["company_details"] = {"complete": True}
        session_data["company_finances"] = {"complete": True}

        fake_request = self.get_request_mock("/plea/your_finances")
        request_context = RequestContext(fake_request)

        form = PleaOnlineForms(session_data, "your_finances")

        form.load(request_context)

        test_data = {
            "you_are": "Other",
            "other_details": "woo woo woo",
            "other_pay_amount": "100",
            "other_hardship": False
        }

        form.save(test_data, request_context)

        form = PleaOnlineForms(session_data, "review")

        form.load(request_context)

        response = form.render()

        self.assertNotContains(response, "<<SHOWINGEXPENSES>>")


class TestYourExpensesStage(TestMultiPleaFormBase):

    def setUp(self):

        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="test@test.com",
            submission_email="test@test.com",
            plp_email="test@test.com",
            enabled="test@test.com",
            test_mode=False)

        hearing_date = datetime.date.today()+datetime.timedelta(30)

        self.fake_request = self.get_request_mock("/plea/your_finances")
        self.request_context = RequestContext(self.fake_request)

        self.test_data = {
            "case": {
                "complete": True,
                "date_of_hearing": hearing_date.strftime("%Y-%m-%d"),
                "urn": "06/AA/0000000/00",
                "number_of_charges": 1,
                "plea_made_by": "Defendant"
            },
            "your_details": {
                "complete": True
            },
            "plea": {
                "complete": True,
                "data": [
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something"
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something"
                    },
                    {
                        "guilty": "guilty",
                        "guilty_extra": "something"
                    }
                ]
            },
            "your_finances":  {
                "complete": True
            },
            "your_expenses": {
                "total_household_expenses": 999
            },
            "review": {
                "complete": True
            }
        }

    def test_hardship_form_requires_validation(self):

        form = PleaOnlineForms(self.test_data, "hardship")

        form.load(self.request_context)

        form.save({}, self.request_context)

        response = form.render()

        self.assertEquals(response.status_code, 200)

    def test_household_expenses_form_requires_validation(self):

        form = PleaOnlineForms(self.test_data, "household_expenses")

        form.load(self.request_context)

        form.save({}, self.request_context)

        response = form.render()

        self.assertEquals(response.status_code, 200)
