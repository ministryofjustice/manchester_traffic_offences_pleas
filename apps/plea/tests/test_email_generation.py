# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

from django.test import TestCase
from django.core import mail

from apps.plea.attachment import TemplateAttachmentEmail

from ..email import send_plea_email
from ..models import Case, CourtEmailCount, Court


class EmailGenerationTests(TestCase):

    def setUp(self):
        mail.outbox = []

        self.court_obj = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="test@test.com",
            submission_email="test@test.com",
            plp_email="test@test.com",
            enabled=True,
            test_mode=False)

        self.test_data_defendant = {"notice_type": {"sjp": False},
                                    "case": {"urn": "06xcvx89",
                                             "date_of_hearing": "2014-06-30",
                                             "contact_deadline": "2014-06-30",
                                             "number_of_charges": 2,
                                             "plea_made_by": "Defendant"},
                                    "your_details": {"updated_address": "Some place",
                                                     "first_name": "v",
                                                     "last_name": "cx",
                                                     "contact_number": "07000000000",
                                                     "date_of_birth": "1970-01-01"},
                                    "plea": {"data": [{"guilty": "guilty", "guilty_extra": "test1"},
                                                       {"guilty": "guilty", "guilty_extra": "test2"}]},
                                    "review": {"receive_email_updates": True,
                                               "email": "test@test.com",
                                               "understand": True}}

        self.test_data_company = {"notice_type": {"sjp": False},
                                  "case": {"urn": "06xcvx89",
                                           "date_of_hearing": "2014-06-30",
                                           "contact_deadline": "2014-06-30",
                                           "number_of_charges": 2,
                                           "plea_made_by": "Company representative"},
                                  "your_details": {"complete": True,
                                                   "skipped": True},
                                  "company_details": {"company_name": "some company plc",
                                                      "updated_address": "some place plc",
                                                      "first_name": "John",
                                                      "last_name": "Smith",
                                                      "position_in_company": "a director",
                                                      "contact_number": "0800 SOMECOMPANY"},
                                  "plea": {"data": [{"guilty": "guilty", "guilty_extra": "test1"},
                                                     {"guilty": "guilty", "guilty_extra": "test2"}]},
                                  "review": {"receive_email_updates": True,
                                             "email": "test@test.com",
                                             "understand": True}}

    def test_template_attachment_sends_email(self):
        email_context = {"URN": "062B3C4D5E"}
        email = TemplateAttachmentEmail("test_from@example.org",
                                        "test.html",
                                        "emails/attachments/plea_email.html",
                                        email_context,
                                        "<p>Test Content</p><br><p>{{ URN }}</p>")

        email.send(["test_to@example.org", ],
                   "Subject line",
                   "Body Text")

        self.assertEqual(mail.outbox[0].subject, "Subject line")
        self.assertEqual(mail.outbox[0].body, "Body Text")

    def test_plea_email_sends(self):
        send_plea_email(self.test_data_defendant)

        self.assertEqual(len(mail.outbox), 3)

    def test_plea_email_adds_to_court_stats(self):
        send_plea_email(self.test_data_defendant)

        court_stats_count = CourtEmailCount.objects.count()

        self.assertEqual(court_stats_count, 1)

    def test_sjp_plea_email_adds_to_court_stats(self):
        self.test_data_defendant["notice_type"]["sjp"] = True
        self.test_data_defendant["case"]["posting_date"] = "2014-06-30"
        del self.test_data_defendant["case"]["date_of_hearing"]

        send_plea_email(self.test_data_defendant)

        court_stats_count = CourtEmailCount.objects.count()

        self.assertEqual(court_stats_count, 1)

    def test_plea_email_body_contains_plea_and_count_ids(self):
        send_plea_email(self.test_data_defendant)

        case_obj = Case.objects.all().order_by('-id')[0]
        count_obj = CourtEmailCount.objects.latest('date_sent')

        matches = re.search("<<<makeaplea-ref:\s*(\d+)/(\d+)>>>", mail.outbox[0].body)

        try:
            matches.groups()
        except AttributeError:
            self.fail('Body makeaplea-ref tag not found!')

        case_id, count_id = matches.groups()

        self.assertEqual(int(case_id), case_obj.id)
        self.assertEqual(int(count_id), count_obj.id)

    def test_user_confirmation_sends_email(self):
        send_plea_email(self.test_data_defendant)

        self.assertEqual(len(mail.outbox), 3)
        self.assertIn(self.test_data_defendant['case']['urn'].upper(), mail.outbox[-1].body)
        self.assertIn(self.test_data_defendant['case']['urn'].upper(), mail.outbox[-1].alternatives[0][0])
        self.assertIn(self.test_data_defendant['review']['email'], mail.outbox[-1].to)

    def test_user_confirmation_sends_no_email(self):
        self.test_data_defendant.update({"review": {"receive_email_updates": False,
                                                    "email": "test@test.com",
                                                    "understand": True}})
        send_plea_email(self.test_data_defendant)

        self.assertEqual(len(mail.outbox), 2)

    def test_user_confirmation_for_company_uses_correct_email_address(self):
        send_plea_email(self.test_data_company)

        self.assertEqual(len(mail.outbox), 3)
        self.assertIn(self.test_data_company['case']['urn'].upper(), mail.outbox[-1].body)
        self.assertIn(self.test_data_company['case']['urn'].upper(), mail.outbox[-1].alternatives[0][0])
        self.assertIn(self.test_data_company['review']['email'], mail.outbox[-1].to)

    def test_email_addresses_from_court_model(self):
        send_plea_email(self.test_data_defendant)

        self.assertEqual(len(mail.outbox), 3)

        to_emails = [item.to[0] for item in mail.outbox]

        self.assertIn(self.court_obj.submission_email, to_emails)
        self.assertIn(self.court_obj.plp_email, to_emails)

    def test_plp_email_doesnt_send_when_court_field_blank(self):
        self.court_obj.plp_email = ""
        self.court_obj.save()

        send_plea_email(self.test_data_defendant)

        self.assertEqual(len(mail.outbox), 2)

    def test_anon_stats_not_added_when_court_in_test_mode(self):
        self.court_obj.test_mode = True
        self.court_obj.save()

        anon_total = CourtEmailCount.objects.all().count()

        send_plea_email(self.test_data_defendant)

        self.assertEquals(anon_total, CourtEmailCount.objects.all().count())
