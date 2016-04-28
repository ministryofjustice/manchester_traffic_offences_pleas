from collections import OrderedDict
import datetime as dt

from django.test import TestCase

from apps.plea.models import Case, Court
from apps.plea.stages import URNEntryStage


class BaseTestCase(TestCase):
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
            validate_urn=True,
            display_case_data=True,
            test_mode=False)

        self.case = Case.objects.create(
            urn="06AA0000015",
            case_number="12345",
            ou_code="06",
            initiation_type="J",
            imported=True,
            extra_data={"PostCode": "M60 1PR",
                        "Surname": "Marsh",
                        "Forename1": "Frank"})

        self.case.offences.create(
            offence_code="RT12345",
            offence_short_title="Some Traffic problem",
            offence_wording="On the 30th December 2015 ... blah blah",
            offence_seq_number="001"
        )

        self.case.offences.create(
            offence_code="RT12346",
            offence_short_title="Some Other Traffic problem",
            offence_wording="On the 31st December 2015 ... blah blah",
            offence_seq_number="002")

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


class PleaModelTestCase(TestCase):

    def setUp(self):
        super(PleaModelTestCase, self).setUp()

    def test_can_auth_no_dob(self):
        case = Case(extra_data=dict(PostCode="WA5 555"))

        self.assertTrue(case.can_auth())

    def test_can_auth_no_postcode(self):
        case = Case(extra_data=dict(DOB="2015-11-11"))

        self.asserTrue(case.can_auth())

    def test_can_auth_no_dob_and_no_password(self):
        case = Case(extra_data={})

        self.assertFalse(case.can_auth())

    def test_authenticate_invalid_number_of_charges(self):
        self.assertFalse(self.case.authenticate(5, "M60 1PR", None))

    def test_authenticate_invalid_postcode(self):
        self.assertFalse(self.case.authenticate(1, "WA1 1UD", None))

    def test_authenticate_invalid_dob(self):
        self.case.extra_data["DOB"] = "1979-03-11"
        self.assertFalse(self.case.authenticate(1, None, dt.date(2016, 10, 5)))

    def test_authenticate_valid_dob(self):
        self.case.extra_data["DOB"] = "1979-03-11"
        self.assertTrue(self.case.authenticate(1, None, dt.date(2016, 3, 11)))

    def test_authenticate_valid_postcode(self):
        self.assertTrue(self.case.authenticate(1, "m601pr"))

    def test_auth_field_dob(self):
        self.assertEquals(self.case.auth_field(), "PostCode")

    def test_auth_field_postcode(self):
        self.case.extra_data["DOB"] = "1979-03-11"

        self.assertEquals(self.case.auth_field(), "DOB")


class URNStageWithURNValidation(TestCase):

    def setUp(self):
        super(URNStageWithURNValidation, self).setUp()

    def test_missing_dob_and_postcode_cannot_continue(self):
        del self.case.extra_data["PostCode"]

        assert "DOB" not in self.case.extra_data

        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})

        import pdb; pdb.set_trace()

    def test_multiple_defendants_per_urn_cannot_continue(self):
        pass

    def test_urn_not_in_database_cannot_continue(self):
        pass


class AuthStageWithURNValidationTestCase(TestCase):
    def test_valid_auth_details(self):
        pass

    def test_invalid_auth_details(self):
        pass


class YourDetailsStageWithStrictURNTestCase(TestCase):
    def test_dob_field_present_if_authed_with_postcode(self):
        pass

    def test_dob_field_hidden_if_authed_with_dob(self):
        pass


class CourtEmailWithStrictValidationTestCase(TestCase):
    def test_court_email_includes_dob_when_user_authenticates_with_dob(self):
        pass
