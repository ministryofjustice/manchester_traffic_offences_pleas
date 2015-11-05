from __future__ import absolute_import, unicode_literals
import datetime as dt

from django.test import TestCase

from ..models import CourtEmailCount, UsageStats, Court


def seed_stats(self):
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


class CourtEmailCountManagerTestCase(TestCase):
    def setUp(self):
        seed_stats(self)

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


class CourtEmailCountModelTestCase(TestCase):
    def setUp(self):
        seed_stats(self)

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


    def get_stats_start_date(self):

        totals = CourtEmailCount.objects.get_stats(start="2015-01-12")

        print totals
        self.assertEquals(totals["submissions"], 7)
        self.assertEquals(totals["pleas"], 9)
        self.assertEquals(totals["guilty"], 6)
        self.assertEquals(totals["not_guilty"], 3)


    def get_stats_end_date(self):

        totals = CourtEmailCount.objects.get_stats(end="2015-01-12")

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
        self.assertEqual(stats[0]["stats"]["submissions"], 7)
        self.assertEqual(stats[0]["stats"]["pleas"], 13)
        self.assertEqual(stats[0]["stats"]["guilty"], 8)
        self.assertEqual(stats[0]["stats"]["not_guilty"], 5)


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

class UsageStatsTestCase(TestCase):

    def setUp(self):
        seed_stats(self)

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

