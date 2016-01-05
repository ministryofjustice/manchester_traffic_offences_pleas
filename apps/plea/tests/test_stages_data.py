from collections import OrderedDict
from django.test import TestCase

from ..stages import URNEntryStage
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
            initiation_type="Q")

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

        self.data = {"enter_urn": {},
                     "notice_type": {},
                     "case": {},
                     "complete": {}}

        self.urls = OrderedDict((("enter_urn", "enter_urn"),
                                 ("notice_type", "notice_type"),
                                 ("case", "case"),
                                 ("complete", "complete")))


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


class TestURNStageDataCourtSJP(TestURNStageDataBase):
    def test_data_court_sjp_case_sjp(self):
        """
        Data switched on, court set to SJP, case initiation_type J
        """
        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], True)

    def test_data_court_sjp_case_req(self):
        """
        Data switched on, court set to SJP, case initiation_type Q
        """
        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], False)

    def test_data_court_sjp_case_other(self):
        """
        Data switched on, court set to SJP, case initiation_type C
        """
        self.court.notice_types = "sjp"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], False)


class TestURNStageDataCourtMAP(TestURNStageDataBase):
    def test_data_court_map_case_sjp(self):
        """
        Data switched on, court set to non-SJP, case initiation_type J
        """
        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], True)

    def test_data_court_map_case_req(self):
        """
        Data switched on, court set to non-SJP, case initiation_type Q
        """
        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], False)

    def test_data_court_map_case_other(self):
        """
        Data switched on, court set to non-SJP, case initiation_type C
        """
        self.court.notice_types = "non-sjp"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], False)


class TestURNStageDataCourtBoth(TestURNStageDataBase):
    def test_data_court_both_case_sjp(self):
        """
        Data switched on, court set to both, case initiation_type J
        """
        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "J"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], True)

    def test_data_court_both_case_req(self):
        """
        Data switched on, court set to both, case initiation_type Q
        """
        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "Q"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], False)

    def test_data_court_both_case_other(self):
        """
        Data switched on, court set to both, case initiation_type C
        """
        self.court.notice_types = "both"
        self.court.save()

        self.case.initiation_type = "C"
        self.case.save()

        stage = URNEntryStage(self.urls, self.data)
        stage.save({"urn": "06AA0000015"})
        self.assertEqual(stage.next_step, "case")
        self.assertEqual(self.data["notice_type"]["sjp"], False)
