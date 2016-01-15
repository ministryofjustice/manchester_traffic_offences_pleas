from collections import OrderedDict
from django.test import TestCase

from ..stages import URNEntryStage, AuthenticationStage
from ..models import Court, Case


class TestURNStageDataBase(TestCase):
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
            extra_data={"PostCode": "M60 1PR"})

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
                      "your_finances": {},
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
                      "your_finances": {},
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
                                 ("your_finances", "your_finances"),
                                 ("hardship", "hardship"),
                                 ("household_expenses", "household_expenses"),
                                 ("other_expenses", "other_expenses"),
                                 ("company_details", "company_details"),
                                 ("company_finances", "company_finances"),
                                 ("case", "case"),
                                 ("complete", "complete")))


class TestURNStageBadData(TestURNStageDataBase):
    def test_with_no_extra_data(self):
        stage = AuthenticationStage(self.urls, self.data3)
        stage.save({"postcode": "m601pr", "number_of_charges": 2})
        self.assertEqual(stage.next_step, "notice_type")


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
