from __future__ import absolute_import, unicode_literals
import datetime as dt

from django.test import TestCase

from ..models import CourtEmailCount, UsageStats, Court, Case


class TestStatsBase(TestCase):
    def setUp(self):
        """
        Populates the test DB with test data: 3 Court objects,
        and several CourtEmailCount objects.
        """
        self.court_1 = Court.objects.create(
            court_name="Court 01",
            region_code="01",
            test_mode=False,
            enabled=True, court_address="x", court_telephone="x", court_email="x", submission_email="x")

        self.court_2 = Court.objects.create(
            court_name="Court 02",
            region_code="02",
            test_mode=False,
            enabled=True, court_address="x", court_telephone="x", court_email="x", submission_email="x")

        self.court_3 = Court.objects.create(
            court_name="Court 03, Test mode",
            region_code="03",
            test_mode=True,
            enabled=True, court_address="x", court_telephone="x", court_email="x", submission_email="x")

        """
        Create dummy CourtEmailCount entries. Switching off auto_now_add
        allows the save date to be faked.
        """

        for field in CourtEmailCount._meta.local_fields:
            if field.name == "date_sent":
                field.auto_now_add = False

        # Court 1, week starting 05/01/2015
        CourtEmailCount.objects.create(court=self.court_1, total_pleas=1, total_guilty=1, total_not_guilty=0, date_sent=dt.date(2015, 1, 5), hearing_date=dt.date(2015, 1, 29), sent=True) # 24 days
        CourtEmailCount.objects.create(court=self.court_1, total_pleas=1, total_guilty=0, total_not_guilty=1, date_sent=dt.date(2015, 1, 5), hearing_date=dt.date(2015, 1, 29), sent=True) # 24 days
        CourtEmailCount.objects.create(court=self.court_1, total_pleas=2, total_guilty=2, total_not_guilty=0, date_sent=dt.date(2015, 1, 5), hearing_date=dt.date(2015, 1, 29), sent=True) # 24 days
        CourtEmailCount.objects.create(court=self.court_1, total_pleas=3, total_guilty=2, total_not_guilty=1, date_sent=dt.date(2015, 1, 9), hearing_date=dt.date(2015, 1, 30), sent=True) # 21 days

        # Court 1, week starting 12/01/2015
        CourtEmailCount.objects.create(court=self.court_1, total_pleas=2, total_guilty=1, total_not_guilty=1, date_sent=dt.date(2015, 1, 12), hearing_date=dt.date(2015, 1, 30), sent=True) # 18 days
        CourtEmailCount.objects.create(court=self.court_1, total_pleas=2, total_guilty=1, total_not_guilty=1, date_sent=dt.date(2015, 1, 12), hearing_date=dt.date(2015, 1, 30), sent=True) # 18 days
        CourtEmailCount.objects.create(court=self.court_1, total_pleas=2, total_guilty=1, total_not_guilty=1, date_sent=dt.date(2015, 1, 14), hearing_date=dt.date(2015, 1, 31), sent=True) # 17 days

        # Court 2, week starting 12/01/2015
        CourtEmailCount.objects.create(court=self.court_2, total_pleas=3, total_guilty=3, total_not_guilty=0, date_sent=dt.date(2015, 1, 12), hearing_date=dt.date(2015, 1, 30), sent=True) # 18 days

        # Test court, week starting 12/01/2015
        CourtEmailCount.objects.create(court=self.court_3, total_pleas=3, total_guilty=0, total_not_guilty=3, date_sent=dt.date(2015, 1, 12), hearing_date=dt.date(2015, 1, 30), sent=True)

        for field in CourtEmailCount._meta.local_fields:
            if field.name == "date_sent":
                field.auto_now_add = True


class CourtEmailCountManagerTestCase(TestStatsBase):
    def test_calculate_aggregates(self):

        totals = CourtEmailCount.objects.calculate_aggregates(dt.date(2015, 1, 5), 7)

        self.assertEquals(totals['submissions'], 4)
        self.assertEquals(totals['pleas'], 7)
        self.assertEquals(totals['guilty'], 5)
        self.assertEquals(totals['not_guilty'], 2)

    def test_null_entries_are_zero(self):

        totals = CourtEmailCount.objects.calculate_aggregates(dt.date(2020, 1, 1), 7)

        self.assertEquals(totals['submissions'], 0)
        self.assertEquals(totals['pleas'], 0)
        self.assertEquals(totals['guilty'], 0)
        self.assertEquals(totals['not_guilty'], 0)


class CourtEmailCountModelTestCase(TestStatsBase):
    def test_get_from_context_hearing_date_is_combined_date_and_time(self):
        context = {
            "notice_type": {"sjp": False},
            "plea": {
                "data": {},
            },
            "your_details": {},
            "case": {
                "date_of_hearing": "2014-09-22",
                "contact_deadline": "2014-09-22"
            }
        }
        emailcount = CourtEmailCount()
        emailcount.get_from_context(context, self.court_1)

        self.assertEqual(emailcount.hearing_date, dt.datetime(2014, 9, 22))

    def test_court_email_plea__get_from_context__sc_char_count(self):

        context = {
            "notice_type": {"sjp": False},
            "plea": {
                "data": [
                    {
                        "guilty_extra": "13 chars long",
                        "guilty": "guilty"
                    },
                    {
                        "not_guilty_extra": "16 chars long xx",
                        "guilty": "not_guilty"
                    }
                ],
            },
            "your_details": {
                "national_insurance_number": "xxx",
                "driving_licence_number": "xxx",
                "registration_number": "xxx"
            },
            "case": {
                "date_of_hearing": "2014-09-22",
                "contact_deadline": "2014-09-22",
            },
        }

        email_count = CourtEmailCount()

        email_count.get_from_context(context, self.court_1)

        self.assertEqual(email_count.sc_guilty_char_count, 13)
        self.assertEqual(email_count.sc_not_guilty_char_count, 16)

    def test_get_stats(self):

        totals = CourtEmailCount.objects.get_stats()

        self.assertEquals(totals["submissions"], 8)
        self.assertEquals(totals["pleas"], 16)
        self.assertEquals(totals["guilty"], 11)
        self.assertEquals(totals["not_guilty"], 5)

    def test_get_stats_start_date(self):

        totals = CourtEmailCount.objects.get_stats(start="2015-01-12")

        self.assertEquals(totals["submissions"], 4)
        self.assertEquals(totals["pleas"], 9)
        self.assertEquals(totals["guilty"], 6)
        self.assertEquals(totals["not_guilty"], 3)

    def test_get_stats_end_date(self):

        totals = CourtEmailCount.objects.get_stats(end="2015-01-11")

        self.assertEquals(totals["submissions"], 4)
        self.assertEquals(totals["pleas"], 7)
        self.assertEquals(totals["guilty"], 5)
        self.assertEquals(totals["not_guilty"], 2)

    def test_get_stats_by_hearing_date(self):

        stats = CourtEmailCount.objects.get_stats_by_hearing_date()

        self.assertEqual(len(stats), 3)

    def test_get_stats_by_hearing_date_1_day(self):

        stats = CourtEmailCount.objects.get_stats_by_hearing_date(days=1)

        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]["hearing_day"], dt.date(2015, 1, 29))
        self.assertEqual(stats[0]["submissions"], 3)
        self.assertEqual(stats[0]["pleas"], 4)
        self.assertEqual(stats[0]["guilty"], 3)
        self.assertEqual(stats[0]["not_guilty"], 1)

    def test_get_stats_by_hearing_date_1_day_date_specified(self):

        stats = CourtEmailCount.objects.get_stats_by_hearing_date(days=1, start_date="2015-01-30")

        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]["hearing_day"], dt.date(2015, 1, 30))
        self.assertEqual(stats[0]["submissions"], 4)
        self.assertEqual(stats[0]["pleas"], 10)
        self.assertEqual(stats[0]["guilty"], 7)
        self.assertEqual(stats[0]["not_guilty"], 3)

    def test_get_stats_by_court(self):

        stats = CourtEmailCount.objects.get_stats_by_court()

        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["court_name"], "Court 01")
        self.assertEqual(stats[0]["submissions"], 7)
        self.assertEqual(stats[0]["pleas"], 13)
        self.assertEqual(stats[0]["guilty"], 8)
        self.assertEqual(stats[0]["not_guilty"], 5)

    def test_get_stats_by_court_with_start_date(self):

        stats = CourtEmailCount.objects.get_stats_by_court(start="2015-01-12")

        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["court_name"], "Court 01")
        self.assertEqual(stats[0]["submissions"], 3)
        self.assertEqual(stats[0]["pleas"], 6)
        self.assertEqual(stats[0]["guilty"], 3)
        self.assertEqual(stats[0]["not_guilty"], 3)

    def test_get_stats_by_court_with_end_date(self):

        stats = CourtEmailCount.objects.get_stats_by_court(end="2015-01-11")

        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["court_name"], "Court 01")
        self.assertEqual(stats[0]["submissions"], 4)
        self.assertEqual(stats[0]["pleas"], 7)
        self.assertEqual(stats[0]["guilty"], 5)
        self.assertEqual(stats[0]["not_guilty"], 2)

    def test_get_stats_days_from_hearing(self):

        stats = CourtEmailCount.objects.get_stats_days_from_hearing()

        self.assertEqual(len(stats), 60)
        self.assertEqual(stats[24], 3)
        self.assertEqual(stats[21], 1)
        self.assertEqual(stats[18], 3)
        self.assertEqual(stats[17], 1)

    def test_get_stats_days_from_hearing_limit_5_days(self):
        stats = CourtEmailCount.objects.get_stats_days_from_hearing(limit=5)

        self.assertEqual(len(stats), 5)


class UsageStatsTestCase(TestStatsBase):
    def setUp(self):
        super(UsageStatsTestCase, self).setUp()
        # wednesday
        self.to_date = dt.date(2015, 01, 21)

    def test_calculate_weekly_stats(self):

        UsageStats.objects.create(start_date=dt.date(2014, 12, 29), online_submissions=0)

        UsageStats.objects.calculate_weekly_stats(to_date=self.to_date)

        self.assertEquals(UsageStats.objects.all().count(), 3)

        wk_, wk1, wk2 = UsageStats.objects.all().order_by('start_date')

        self.assertEquals(wk1.start_date, dt.date(2015, 01, 05))
        self.assertEquals(wk1.online_submissions, 4)

        self.assertEquals(wk2.start_date, dt.date(2015, 01, 12))
        self.assertEquals(wk2.online_submissions, 4)


class TestCourtModel(TestCase):
    def setUp(self):
        self.court = Court.objects.create(
            region_code="51",
            ou_code="12345",
            court_name="Test Court",
            court_address="28 Court Street",
            court_telephone="0800 Court",
            court_email="test@court.com",
            court_language="en",
            submission_email="test@court.com",
            enabled=True)

        self.court2 = Court.objects.create(
            region_code="61",
            ou_code="54321",
            court_name="Test Court 2",
            court_address="29 Court Street",
            court_telephone="0800 Court",
            court_email="test@court.com",
            court_language="en",
            submission_email="test@court.com",
            enabled=True)

        self.case = Case.objects.create(
            ou_code="54321",
            imported=True,
            urn="51XX0000000")

    def test_manager_get_by_urn(self):
        self.assertEquals(self.court.id, Court.objects.get_by_urn("51/xx/00000/00").id)

    def test_manager_get_by_urn_no_match(self):
        self.court.enabled = False
        self.court.save()

        with self.assertRaises(Court.DoesNotExist):
            Court.objects.get_by_urn("51/xx/00000/00")

    def test_get_by_court_with_ou_code(self):

        self.assertEquals(self.court.id, Court.objects.get_court("99/xx/00000/00", ou_code="12345").id)

    def test_get_by_court_ou_code_no_match(self):
        self.assertEquals(self.court.id, Court.objects.get_court("51/xx/00000/00", ou_code="99999").id)

    def test_get_by_court_ou_code_and_urn_no_match(self):
        with self.assertRaises(Court.DoesNotExist):
            Court.objects.get_court("99/xx/00000/00", ou_code="9999999")

    def test_get_court_dx_ou_code_different_court(self):

        court = Court.objects.get_court_dx(self.case.urn)

        self.assertEquals(self.court2.id, court.id)

    def test_get_court_dx_no_case(self):

        court = Court.objects.get_court_dx("51/AA/00000/00")

        self.assertEquals(self.court.id, court.id)

    def test_get_court_dx_duplicate_cases(self):
        """
        IF there's multiple URNs (e.g. multiple defendants per URN resulting
        in multiple cases in the DB with the same URN) then we drop back to URN
        based matching
        """

        self.case.id = None
        self.case.save()

        court = Court.objects.get_court_dx(self.case.urn)

        self.assertEquals(court.id, self.court.id)



