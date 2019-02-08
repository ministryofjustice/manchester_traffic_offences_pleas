from mock import Mock, patch
from unittest import skip

from collections import OrderedDict
from django.utils import translation

from django.test import TestCase, Client
from django.test.client import RequestFactory
from collections import namedtuple

from ..stages import URNEntryStage, AuthenticationStage, PleaStage
from ..models import Court, Case, Offence


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


class TestURNStageDataBase(TestCaseBase):

    def setUp(self):
        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            display_case_data=True,
            test_mode=False)

        self.case = Case.objects.create(
            urn="06AA0000015",
            case_number="12345",
            ou_code="06",
            initiation_type="Q",
            extra_data={"PostCode": "M60 1PR",
                        "Surname": "Marsh",
                        "Forename1": "Frank"})

        self.case.offences.create(
            offence_code="RT12345",
            offence_short_title="Some Traffic problem",
            offence_short_title_welsh="WELSH-SHORT-TITLE",
            offence_wording="On the 30th December 2015 ... blah blah",
            offence_wording_welsh="WELSH-OFFENCE-WORDING",
            offence_seq_number="001"
        )

        self.case.offences.create(
            offence_code="RT12346",
            offence_short_title="Some Other Traffic problem",
            offence_short_title_welsh="WELSH-SHORT-TITLE",
            offence_wording="On the 31st December 2015 ... blah blah",
            offence_wording_welsh="WELSH-OFFENCE-WORDING",
            offence_seq_number="002"
        )

        self.case_no_data = Case.objects.create(
            urn="06AA0000115",
            case_number="12346",
            ou_code="06",
            initiation_type="Q")

        self.case_no_data.offences.create(
            offence_code="RT12345",
            offence_short_title="Some Traffic problem",
            offence_wording="On the 30th December 2015 ... blah blah",
            offence_seq_number="001"
        )

        self.case_no_data.offences.create(
            offence_code="RT12346",
            offence_short_title="Some Other Traffic problem",
            offence_wording="On the 31st December 2015 ... blah blah",
            offence_seq_number="002"
        )

        self.data = {"enter_urn": {},
                     "notice_type": {},
                     "your_details": {},
                     "company_details": {},
                     "case": {},
                     "complete": {}}

        self.data2 = {"enter_urn": {},
                      "notice_type": {},
                      "your_details": {},
                      "your_status": {},
                      "your_employment": {},
                      "your_self_employment": {},
                      "your_out_of_work_benefits": {},
                      "about_your_income": {},
                      "your_benefits": {},
                      "your_pension_credit": {},
                      "your_income": {},
                      "hardship": {},
                      "household_expenses": {},
                      "other_expenses": {},
                      "company_details": {},
                      "company_finances": {},
                      "case": {"urn": "06AA0000015"},
                      "complete": {}}

        self.data3 = {"enter_urn": {},
                      "notice_type": {},
                      "your_details": {},
                      "your_status": {},
                      "your_employment": {},
                      "your_self_employment": {},
                      "your_out_of_work_benefits": {},
                      "about_your_income": {},
                      "your_benefits": {},
                      "your_pension_credit": {},
                      "your_income": {},
                      "hardship": {},
                      "household_expenses": {},
                      "other_expenses": {},
                      "company_details": {},
                      "company_finances": {},
                      "case": {"urn": "06AA0000115"},
                      "complete": {}}

        self.urls = OrderedDict((("enter_urn", "enter_urn"),
                                 ("your_case_continued", "your_case_continued"),
                                 ("notice_type", "notice_type"),
                                 ("your_details", "your_details"),
                                 ("your_status", "your_status"),
                                 ("your_employment", "your_employment"),
                                 ("your_self_employment", "your_self_employment"),
                                 ("your_out_of_work_benefits", "your_out_of_work_benefits"),
                                 ("about_your_income", "about_your_income"),
                                 ("your_benefits", "your_benefits"),
                                 ("your_pension_credit", "your_pension_credit"),
                                 ("your_income", "your_income"),
                                 ("hardship", "hardship"),
                                 ("household_expenses", "household_expenses"),
                                 ("other_expenses", "other_expenses"),
                                 ("company_details", "company_details"),
                                 ("company_finances", "company_finances"),
                                 ("case", "case"),
                                 ("complete", "complete")))

        self.request_context = namedtuple('C', 'request')(RequestFactory().get('/dummy'))


class TestURNStageNoData(TestURNStageDataBase):
    def test_no_data_court_sjp(self):
        """
        Data switched off, court set to SJP
        """
        self.court.notice_types = "sjp"
        self.court.display_case_data = False
        self.court.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], True)

    def test_no_data_court_map(self):
        """
        Data switched off, court set to non-SJP
        """
        self.court.notice_types = "non-sjp"
        self.court.display_case_data = False
        self.court.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], False)

    def test_no_data_court_both(self):
        """
        Data switched off, court set to both
        """
        self.court.notice_types = "both"
        self.court.display_case_data = False
        self.court.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "notice_type")

    def test_no_postcode_drops_user_into_non_validated_route(self):

        del self.case.extra_data["PostCode"]
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "notice_type")


class TestURNStageDuplicateCases(TestURNStageDataBase):

    def setUp(self):
        translation.activate('en')
        super(TestURNStageDuplicateCases, self).setUp()
        self.case.pk = None
        self.case.save()

    @skip("Not sure why this test exists - or why we'd have duplicate cases"
          "with the same name? Leaving in place in case it becomes relevant")
    def test_duplicate_cases_same_name_continues(self):
        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})

        response = stage.render(self.get_request_mock(), self.request_context)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(stage.next_step, "your_case_continued")

    def test_duplicate_cases_different_names_drops_out(self):
        self.case.extra_data["Forename1"] = "Freda"
        self.case.save()
        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": self.case.urn})

        response = stage.render(self.get_request_mock(), self.request_context)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(stage.next_step, "notice_type")


class TestAuthStageSJP(TestURNStageDataBase):
    def test_data_court_sjp_case_sjp(self):
        """
        Data switched on, court set to SJP, case initiation_type J
        """
        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], True)

    def test_data_court_sjp_case_req(self):
        """
        Data switched on, court set to SJP, case initiation_type Q
        """
        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)

    def test_data_court_sjp_case_other(self):
        """
        Data switched on, court set to SJP, case initiation_type C
        """
        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)


class TestAuthStageMAP(TestURNStageDataBase):
    def test_data_court_map_case_sjp(self):
        """
        Data switched on, court set to non-SJP, case initiation_type J
        """
        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], True)

    def test_data_court_map_case_req(self):
        """
        Data switched on, court set to non-SJP, case initiation_type Q
        """
        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)

    def test_data_court_map_case_other(self):
        """
        Data switched on, court set to non-SJP, case initiation_type C
        """
        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)


class TestAuthStageBoth(TestURNStageDataBase):
    def test_data_court_both_case_sjp(self):
        """
        Data switched on, court set to both, case initiation_type J
        """
        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], True)

    def test_data_court_both_case_req(self):
        """
        Data switched on, court set to both, case initiation_type Q
        """
        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)

    def test_data_court_both_case_other(self):
        """
        Data switched on, court set to both, case initiation_type C
        """
        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "your_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)


class TestAuthStage(TestURNStageDataBase):
    def test_wrong_entry_data_disabled_both(self):
        """
        Data switched on, court set to both, case initiation_type J
        """
        self.court.notice_types = "both"
        self.court.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m331pr", "number_of_charges": 5})
        self.assertEqual(stage.next_step, "notice_type")

    def test_wrong_entry_data_disabled_SJP(self):
        """
        Data switched on, court set to both, case initiation_type J
        """
        self.court.notice_types = "sjp"
        self.court.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m331pr", "number_of_charges": 5})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data2["notice_type"]["sjp"], True)

    def test_wrong_entry_data_disabled_MAP(self):
        """
        Data switched on, court set to both, case initiation_type J
        """
        self.court.notice_types = "non-sjp"
        self.court.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m331pr", "number_of_charges": 5})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)


class TestCompanyAuthStageSJP(TestURNStageDataBase):
    def test_data_court_sjp_case_sjp(self):
        """
        Data switched on, court set to SJP, case initiation_type J
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], True)

    def test_data_court_sjp_case_req(self):
        """
        Data switched on, court set to SJP, case initiation_type Q
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)

    def test_data_court_sjp_case_other(self):
        """
        Data switched on, court set to SJP, case initiation_type C
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)


class TestCompanyAuthStageMAP(TestURNStageDataBase):
    def test_data_court_map_case_sjp(self):
        """
        Data switched on, court set to non-SJP, case initiation_type J
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], True)

    def test_data_court_map_case_req(self):
        """
        Data switched on, court set to non-SJP, case initiation_type Q
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)

    def test_data_court_map_case_other(self):
        """
        Data switched on, court set to non-SJP, case initiation_type C
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)


class TestCompanyAuthStageBoth(TestURNStageDataBase):
    def test_data_court_both_case_sjp(self):
        """
        Data switched on, court set to both, case initiation_type J
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], True)

    def test_data_court_both_case_req(self):
        """
        Data switched on, court set to both, case initiation_type Q
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)

    def test_data_court_both_case_other(self):
        """
        Data switched on, court set to both, case initiation_type C
        """
        self.case.extra_data["OrganisationName"] = "Marsh Incorporated"
        self.case.save()

        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = AuthenticationStage(self.urls, self.data2)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "company_details")
        self.assertEqual(self.data2["notice_type"]["sjp"], False)


class TestPleaAuthStage(TestURNStageDataBase):
    def test_offences_shown_with_dx(self):

        self.data["dx"] = True
        self.data["plea"] = {}
        self.data["case"]["urn"] = "06AA0000015"

        stage = PleaStage(self.urls, self.data)
        stage.load_forms({})

        self.assertIsInstance(stage.form.case_data, Offence)

    def test_offences_not_shown_with_no_dx(self):

        self.data["dx"] = False
        self.data["plea"] = {}

        stage = PleaStage(self.urls, self.data)
        stage.load_forms({})

        self.assertFalse(getattr(stage.form, "case_data", False))

    @patch("django.utils.translation.get_language", return_value='cy')
    def test_offence_data_is_displayed_in_welsh(self, get_language):

        self.data["dx"] = True
        self.data["plea"] = {}
        self.data["case"]["urn"] = "06AA0000015"

        stage = PleaStage(self.urls, self.data)
        stage.load_forms({})
        response = stage.render(self.get_request_mock(), self.request_context)

        offence = self.case.offences.all().first()

        self.assertContains(response, offence.offence_short_title_welsh.encode("utf-8"))
        self.assertContains(response, offence.offence_wording_welsh.encode("utf-8"))

    @patch("django.utils.translation.get_language", return_value='cy')
    def test_offence_data_falls_back_to_en_when_cy_data_is_not_available(self, get_language):

        offence = self.case.offences.all().first()

        offence.offence_short_title_welsh = None
        offence.offence_wording_welsh = None
        offence.save()

        self.data["dx"] = True
        self.data["plea"] = {}
        self.data["case"]["urn"] = "06AA0000015"

        stage = PleaStage(self.urls, self.data)
        stage.load_forms({})
        response = stage.render(self.get_request_mock(), self.request_context)

        self.assertContains(response, offence.offence_short_title.encode("utf-8"))
        self.assertContains(response, offence.offence_wording.encode("utf-8"))


class TestURNSubmissionFailureMessage(TestCase):
    def setUp(self):
        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            display_case_data=True,
            validate_urn=True,
            test_mode=False)

        self.case = Case.objects.create(
            urn="06YY0000000",
            imported=True
        )

        self.client = Client()

    def test_single_failure_no_message(self):
        response = self.client.post('/plea/enter_urn/', data=dict(urn="06xx0000000"))

        self.assertContains(response, "You need to fix the errors on this page before continuing.")
        self.assertNotContains(response, "Your reference number has not been recognised")

    def test_message_appears_after_multiple_failures(self):

        for i in range(3):
            response = self.client.post('/plea/enter_urn/', data=dict(urn="06xx0000000"))

        self.assertContains(response, "Your reference number has not been recognised")


