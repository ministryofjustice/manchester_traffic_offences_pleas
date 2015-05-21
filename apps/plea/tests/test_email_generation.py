# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

from django.test import TestCase
from django.core import mail

from ..email import TemplateAttachmentEmail, send_plea_email
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

    def test_template_attachment_sends_email(self):
        email_context = {"URN": "062B3C4D5E"}
        email = TemplateAttachmentEmail("test_from@example.org",
                                        "test.html",
                                        "plea/plea_email_attachment.html",
                                        email_context,
                                        "<p>Test Content</p><br><p>{{ URN }}</p>")

        email.send(["test_to@example.org", ],
                   "Subject line",
                   "Body Text")

        self.assertEqual(mail.outbox[0].subject, "Subject line")
        self.assertEqual(mail.outbox[0].body, "Body Text")

    def test_plea_email_sends(self):
        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "06xcvx89",
                                 "number_of_charges": 2,
                                 "plea_made_by": "Defendant"},
                        "your_details": {"first_name": "v", "last_name": "cx", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx",
                                         "email": "test@test.com"},
                        "plea": {"PleaForms": [{"guilty_extra": "test1", "guilty": "guilty"},
                                               {"guilty_extra": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 3)

    def test_plea_email_body_contains_plea_and_count_ids(self):
        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "06xcvx89",
                                 "number_of_charges": 2,
                                 "plea_made_by": "Defendant"},
                        "your_details": {"first_name": "v", "last_name": "cx", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx",
                                         "email": "test@test.com"},
                        "plea": {"PleaForms": [{"guilty_extra": "test1", "guilty": "guilty"},
                                               {"guilty_extra": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

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
        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "06xcvx89",
                                 "number_of_charges": 2,
                                 "plea_made_by": "Defendant"},
                        "your_details": {"first_name": "v", "last_name": "cx", "email": "lyndon@antlyn.com", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx"},
                        "plea": {"PleaForms": [{"guilty_extra": "test1", "guilty": "guilty"},
                                               {"guilty_extra": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertIn(context_data['case']['urn'].upper(), mail.outbox[-1].body)
        self.assertIn(context_data['case']['urn'].upper(), mail.outbox[-1].alternatives[0][0])
        self.assertIn(context_data['your_details']['email'], mail.outbox[-1].to)

    def test_user_confirmation_for_company_uses_correct_email_address(self):
        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "06xcvx89",
                                 "number_of_charges": 2,
                                 "plea_made_by": "Company representative"},
                        "your_details": {
                            "complete": True,
                            "skipped": True
                        },
                        "company_details": {
                            "company_name": "some company plc",
                            "updated_address": "some place plc",
                            "first_name": "John",
                            "last_name": "Smith",
                            "position_in_company": "a director",
                            "contact_number": "0800 SOMECOMPANY",
                            "email": "test@companyemail.com"
                        },
                        "plea": {"PleaForms": [{"guilty_extra": "test1", "guilty": "guilty"},
                                               {"guilty_extra": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)
        self.assertIn(context_data['case']['urn'].upper(), mail.outbox[-1].body)
        self.assertIn(context_data['case']['urn'].upper(), mail.outbox[-1].alternatives[0][0])
        self.assertIn(context_data['company_details']['email'], mail.outbox[-1].to)

    def test_email_addresses_from_court_model(self):

        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "06xcvx89",
                                 "number_of_charges": 2,
                                 "plea_made_by": "Defendant"},
                        "your_details": {"first_name": "v", "last_name": "cx", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx",
                                         "email": "test@test.com"},
                        "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"},
                                               {"mitigations": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 3)

        to_emails = [item.to[0] for item in mail.outbox]

        self.assertIn(self.court_obj.submission_email, to_emails)
        self.assertIn(self.court_obj.plp_email, to_emails)

    def test_plp_email_doesnt_send_when_court_field_blank(self):

        self.court_obj.plp_email = ""
        self.court_obj.save()

        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "06xcvx89",
                                 "number_of_charges": 2,
                                 "plea_made_by": "Defendant"},
                        "your_details": {"first_name": "v", "last_name": "cx", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx",
                                         "email": "test@test.com"},
                        "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"},
                                               {"mitigations": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

        self.assertEqual(len(mail.outbox), 2)

    def test_anon_stats_not_added_when_court_in_test_mode(self):

        self.court_obj.test_mode = True
        self.court_obj.save()

        anon_total = CourtEmailCount.objects.all().count()

        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "06xcvx89",
                                 "number_of_charges": 2,
                                 "plea_made_by": "Defendant"},
                        "your_details": {"first_name": "v", "last_name": "cx", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx",
                                         "email": "test@test.com"},
                        "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"},
                                               {"mitigations": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

        self.assertEquals(anon_total, CourtEmailCount.objects.all().count())