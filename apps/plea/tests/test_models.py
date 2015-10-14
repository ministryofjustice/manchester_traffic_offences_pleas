from __future__ import absolute_import, unicode_literals
import datetime as dt

from django.test import TestCase

from ..models import CourtEmailCount, UsageStats, Court


class CourtEmailCountModelTestCase(TestCase):
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

    def test_get_from_context_hearing_date_is_combined_date_and_time(self):
        context = {
            "plea": {
                "data": {},
            },
            "your_details": {
                "national_insurance_number": "xxx",
                "driving_licence_number": "xxx",
                "registration_number": "xxx"
            },
            "case": {
                "date_of_hearing": "2014-09-22",
                "contact_deadline": "2014-09-22"
            }
        }
        emailcount = CourtEmailCount()
        emailcount.get_from_context(context, self.court)

        self.assertEqual(emailcount.hearing_date, dt.datetime(2014, 9, 22, 0, 0, 0))

    def test_get_stats_by_hearing_date(self):
        """
        A blanket unit test to confirm that this method returns
        the correct results
        """

        tomorrow = dt.datetime.today() + dt.timedelta(1)

        CourtEmailCount(court=self.court,
                        date_sent=tomorrow,
                        total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        sent=True,
                        hearing_date=tomorrow).save()

        CourtEmailCount(court=self.court,
                        date_sent=tomorrow,
                        total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        sent=True,
                        hearing_date=tomorrow).save()

        CourtEmailCount(court=self.court,
                        date_sent=tomorrow,
                        total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        sent=True,
                        hearing_date=tomorrow+dt.timedelta(1)).save()

        stats = CourtEmailCount.objects.get_stats_by_hearing_date(days=1)

        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]['hearing_day'], tomorrow.date())

        self.assertEqual(stats[0]['submissions'], 2)
        self.assertEqual(stats[0]['guilty'], 2)
        self.assertEqual(stats[0]['not_guilty'], 2)

    def test_court_email_plea__get_from_context__sc_char_count(self):

        context = {
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

        email_count.get_from_context(context, self.court)

        self.assertEqual(email_count.sc_guilty_char_count, 13)
        self.assertEqual(email_count.sc_not_guilty_char_count, 16)

class UsageStatsTestCase(TestCase):
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

        # wednesday
        self.to_date = dt.date(2015, 01, 21)

        # should be included in entry with start_date of 5/01/2015
        obj = CourtEmailCount()
        obj.court = self.court
        obj.total_pleas = 50
        obj.total_guilty = 25
        obj.total_not_guilty = 5
        obj.hearing_date = dt.date(2015, 01, 05)
        obj.save()

        # should be included in entry with start_date of 5/01/2015
        obj = CourtEmailCount()
        obj.court = self.court
        obj.total_pleas = 50
        obj.total_guilty = 25
        obj.total_not_guilty = 5
        obj.hearing_date = dt.date(2015, 01, 10)
        obj.save()

        # should be included in entry with start_date of 5/01/2015
        obj = CourtEmailCount()
        obj.court = self.court
        obj.total_pleas = 50
        obj.total_guilty = 25
        obj.total_not_guilty = 5
        obj.hearing_date = dt.date(2015, 01, 10)
        obj.save()

        # should be included in entry with start_date of 5/01/2015
        obj = CourtEmailCount()
        obj.court = self.court
        obj.total_pleas = 50
        obj.total_guilty = 25
        obj.total_not_guilty = 5
        obj.hearing_date = dt.date(2015, 01, 10)
        obj.save()

        # should be included in entry with start_date of 5/01/2015
        obj = CourtEmailCount()
        obj.court = self.court
        obj.total_pleas = 100
        obj.total_guilty = 50
        obj.total_not_guilty = 5
        obj.hearing_date = dt.date(2015, 01, 19)
        obj.save()

        # should be included in entry with start_date of 5/01/2015
        obj = CourtEmailCount()
        obj.court = self.court
        obj.total_pleas = 100
        obj.total_guilty = 50
        obj.total_not_guilty = 5
        obj.hearing_date = dt.date(2015, 01, 19)
        obj.save()

    def test_calculate_aggregates(self):

        totals = CourtEmailCount.objects.calculate_aggregates(dt.date(2015, 1, 5), 7)

        self.assertEquals(totals['submissions'], 4)
        self.assertEquals(totals['pleas'], 200)
        self.assertEquals(totals['guilty'], 100)
        self.assertEquals(totals['not_guilty'], 20)

    def test_null_entries_are_zero(self):

        totals = CourtEmailCount.objects.calculate_aggregates(dt.date(2020, 1, 1), 7)

        self.assertEquals(totals['submissions'], 0)
        self.assertEquals(totals['pleas'], 0)
        self.assertEquals(totals['guilty'], 0)
        self.assertEquals(totals['not_guilty'], 0)

    def test_weekly_stats(self):

        UsageStats.objects.create(start_date=dt.date(2014, 12, 29), online_submissions=0)

        UsageStats.objects.calculate_weekly_stats(to_date=self.to_date)

        self.assertEquals(UsageStats.objects.all().count(), 3)

        wk_, wk1, wk2 = UsageStats.objects.all().order_by('start_date')

        self.assertEquals(wk1.start_date, dt.date(2015, 01, 05))
        self.assertEquals(wk1.online_submissions, 4)

        self.assertEquals(wk2.start_date, dt.date(2015, 01, 12))
        self.assertEquals(wk2.online_submissions, 2)



