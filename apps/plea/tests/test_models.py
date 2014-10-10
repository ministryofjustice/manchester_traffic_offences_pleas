from __future__ import absolute_import, unicode_literals
import datetime as dt 

from django.test import TestCase

from ..models import CourtEmailCount


class CourtEmailCountModelTestCase(TestCase):

    def test_get_from_context_hearing_date_is_combined_date_and_time(self):
        context = {
            "plea": {
                "PleaForms": {},
            },
            "your_details": {
                "national_insurance_number": "xxx",
                "driving_licence_number": "xxx",
                "registration_number": "xxx"
            },
            "case": {
                "date_of_hearing": "2014-09-22",
                "time_of_hearing": "09:15:00"
            }
        }

        emailcount = CourtEmailCount()
        emailcount.get_from_context(context)

        self.assertEquals(emailcount.hearing_date, dt.datetime(2014, 9, 22, 9, 15, 0))

    def test_get_stats_yesterday(self):
        """
        A blanket unit test to confirm this method is returning the correct stats
        """

        now = dt.datetime.today()

        CourtEmailCount(total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=now).save()

        CourtEmailCount(total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=now).save()

        CourtEmailCount(total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=now).save()

        a, b, c = CourtEmailCount.objects.all()

        a.date_sent = now-dt.timedelta(2)
        a.save()

        b.date_sent = now-dt.timedelta(1)
        b.save()

        c.date_sent = now-dt.timedelta(1)
        c.save()

        stats = CourtEmailCount.objects.get_stats()

        self.assertEquals(stats['submissions']['to_date'], 3)
        self.assertEquals(stats['submissions']['yesterday'], 2)

        self.assertEquals(stats['pleas']['to_date']['guilty'], 3)
        self.assertEquals(stats['pleas']['to_date']['not_guilty'], 3)
        self.assertEquals(stats['pleas']['to_date']['total'], 6)

        self.assertEquals(stats['pleas']['yesterday']['guilty'], 2)
        self.assertEquals(stats['pleas']['yesterday']['not_guilty'], 2)
        self.assertEquals(stats['pleas']['yesterday']['total'], 4)


    def test_get_stats_last_week(self):
        now = dt.datetime.today()

        CourtEmailCount(total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=now).save()

        CourtEmailCount(total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=now).save()

        CourtEmailCount(total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=now).save()

        a, b, c = CourtEmailCount.objects.all()

        a.date_sent = now-dt.timedelta(7)
        a.save()

        b.date_sent = now-dt.timedelta(7)
        b.save()

        stats = CourtEmailCount.objects.get_stats()

        self.assertEquals(stats['pleas']['last_week']['guilty'], 2)
        self.assertEquals(stats['pleas']['last_week']['not_guilty'], 2)
        self.assertEquals(stats['pleas']['last_week']['total'], 4)

        self.assertEquals(stats['submissions']['last_week'], 2)

    def test_get_stats_by_hearing_date(self):
        """
        A blanket unit test to confirm that this method returns
        the correct results
        """

        tomorrow = dt.datetime.today() + dt.timedelta(1)

        CourtEmailCount(date_sent=tomorrow,
                        total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=tomorrow).save()

        CourtEmailCount(date_sent=tomorrow,
                        total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=tomorrow).save()

        CourtEmailCount(date_sent=tomorrow,
                        total_pleas=2,
                        total_guilty=1,
                        total_not_guilty=1,
                        hearing_date=tomorrow+dt.timedelta(1)).save()

        stats = CourtEmailCount.objects.get_stats_by_hearing_date(days=1)

        self.assertEquals(len(stats), 1)
        self.assertEquals(stats[0]['hearing_day'], tomorrow.date())

        self.assertEquals(stats[0]['submissions'], 2)
        self.assertEquals(stats[0]['guilty'], 2)
        self.assertEquals(stats[0]['not_guilty'], 2)

    def test_court_email_plea__get_from_context__sc_char_count(self):

        context = {
            "plea": {
                "PleaForms": [
                    {
                        "mitigations": "13 chars long",
                        "guilty": "guilty"
                    },
                    {
                        "mitigations": "16 chars long xx",
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
                "time_of_hearing": "09:15:00"
            },
        }

        email_count = CourtEmailCount()

        email_count.get_from_context(context)

        self.assertEquals(email_count.sc_guilty_char_count, 13)
        self.assertEquals(email_count.sc_not_guilty_char_count, 16)

    def test_court_email_plea__get_from_context__field_counts(self):
        context = {
            "plea": {
                "PleaForms": [
                    {
                        "mitigations": "13 chars long",
                        "guilty": "guilty"
                    },
                    {
                        "mitigations": "16 chars long xx",
                        "guilty": "not_guilty"
                    }
                ],
            },
            "your_details": {
                "national_insurance_number": "xxxxxx",
                "driving_licence_number": "xxx",
                "registration_number": "x"
            },
            "case": {
                "date_of_hearing": "2014-09-22",
                "time_of_hearing": "09:15:00"
            },
        }

        email_count = CourtEmailCount()

        email_count.get_from_context(context)

        self.assertEquals(email_count.national_insurance_char_count, 6)
        self.assertEquals(email_count.driving_licence_char_count, 3)
        self.assertEquals(email_count.registration_char_count, 1)