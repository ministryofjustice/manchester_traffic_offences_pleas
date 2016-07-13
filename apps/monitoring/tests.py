import datetime as dt

from django.test import TestCase

from apps.plea.models import Court, Case, OUCode
from .views import CourtDataView


class TestStatsLogic(TestCase):

    def setUp(self):
        self.court = self._create_court()

        self.court_view = CourtDataView()

    @staticmethod
    def _create_court(**fields):
        ou_codes = fields.pop("ou_codes", [])

        data = dict(
            region_code="20",
            court_name="TEST COURT 1",
            enabled=True,
            court_address="123 Court",
            court_telephone="0800 COURT",
            court_receipt_email="test@test.com",
            submission_email="test@test.com",
            test_mode=False
        )

        data.update(fields)

        court = Court.objects.create(**data)

        for ou_code in ou_codes:
            OUCode.objects.create(court=court, ou_code=ou_code)

        return court

    @staticmethod
    def _create_case(**fields):

        data = dict(
            imported=False,
            ou_code=None,
            completed_on=None
        )

        data.update(fields)

        return Case.objects.create(**data)

    def test_soap_gateway_imported_submissions_count(self):

        self._create_case(urn="20XX0000000",
                          imported=True)
        self._create_case(urn="20XX0000001",
                          imported=False)
        self._create_case(urn="22XX0000001",
                          imported=False)

        stats = self.court_view._get_stats(self.court, dt.date.today())

        self.assertEquals(stats["imported"]["value"], 1)

    def test_completed_submission_count(self):
        self._create_case(urn="20XX0000000",
                          completed_on=dt.datetime.now())
        self._create_case(urn="20XX0000001")

        stats = self.court_view._get_stats(self.court, dt.date.today())

        self.assertEquals(stats["submissions"]["value"], 1)

    def test_unvalidated_submission_count(self):
        self._create_case(urn="20XX0000000",
                          imported=True,
                          completed_on=dt.datetime.now())
        self._create_case(urn="20XX0000001",
                          completed_on=dt.datetime.now())

        stats = self.court_view._get_stats(self.court, dt.date.today())

        self.assertEquals(stats["unvalidated_submissions"]["value"], 1)

    def test_failed_email_sending_count(self):
        self._create_case(urn="20XX0000000",
                          sent=False,
                          completed_on=dt.datetime.now())
        self._create_case(urn="20XX0000001",
                          sent=True,
                          completed_on=dt.datetime.now())

        stats = self.court_view._get_stats(self.court, dt.date.today())

        self.assertEquals(stats["email_failure"]["value"], 1)

    def test_sjp_case_import_count(self):
        self._create_case(urn="20XX0000000",
                          initiation_type="J",
                          completed_on=dt.datetime.now())
        self._create_case(urn="20XX0000001",
                          completed_on=dt.datetime.now())

        stats = self.court_view._get_stats(self.court, dt.date.today())

        self.assertEquals(stats["sjp_count"]["value"], 1)

    def test_completed_on_with_oucode(self):
        """
        If a court specifies ou codes, then only match cases that have that OU code.
        """

        self._create_case(urn="20XX0000000",
                          completed_on=dt.datetime.now(),
                          ou_code="B01CY")
        self._create_case(urn="20XX0000001",
                          completed_on=dt.datetime.now(),
                          ou_code="B01LY")

        OUCode.objects.create(court=self.court, ou_code="B01CY")

        stats = self.court_view._get_stats(self.court, dt.date.today())

        self.assertEquals(stats["submissions"]["value"], 1)



