from datetime import datetime, timedelta
from django.test import TestCase

from plea.models import CourtEmailPlea


class TestClearOldEmailAudit(TestCase):
    @staticmethod
    def create_court_email_plea(hearing_date):
        c = CourtEmailPlea()
        c.dict_sent = {"foo": "bar"}
        c.subject = "FOOBARBAZ"
        c.attachment_text = "<html><body><h1>FOO</h1></body></html>"
        c.body_text = ""
        c.address_from = "from@example.org"
        c.address_to = "to@example.org"
        c.hearing_date = hearing_date
        c.save()

    def test_old_dates_deleted(self):
        today = datetime.today()
        td_day = timedelta(days=2)
        self.create_court_email_plea(today - td_day)
        CourtEmailPlea.objects.delete_old_emails()

        self.assertEqual(CourtEmailPlea.objects.count(), 0)

    def test_new_dates_not_deleted(self):
        today = datetime.today()
        td_day = timedelta(days=2)
        self.create_court_email_plea(today + td_day)
        CourtEmailPlea.objects.delete_old_emails()

        self.assertEqual(CourtEmailPlea.objects.count(), 1)

    def test_old_date_deleted_new_date_not_deleted(self):
        today = datetime.today()
        td_day = timedelta(days=2)
        self.create_court_email_plea(today + td_day)
        self.create_court_email_plea(today - td_day)
        CourtEmailPlea.objects.delete_old_emails()

        self.assertEqual(CourtEmailPlea.objects.count(), 1)

    def test_does_not_clear_email_for_today(self):
        today = datetime.today()
        self.create_court_email_plea(today)
        CourtEmailPlea.objects.delete_old_emails()

        self.assertEqual(CourtEmailPlea.objects.count(), 1)
