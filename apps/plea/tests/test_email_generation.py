# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

from django.test import TestCase
from django.core import mail

from ..email import TemplateAttachmentEmail, send_plea_email
from ..models import Case, CourtEmailCount


class EmailGenerationTests(TestCase):
    def setUp(self):
        mail.outbox = []

    def test_template_attachment_sends_email(self):
        email_context = {"URN": "1A2B3C4D5E"}
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
                                 "urn": "cvxcvx89",
                                 "number_of_charges": 2,
                                 "company_plea": False},
                        "your_details": {"name": "vcx", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx",
                                         "email": "test@test.com"},
                        "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"},
                                               {"mitigations": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data)

        # only expecting 1 email for now, PLP email cancelled for the time being
        self.assertEqual(len(mail.outbox), 3)

    def test_plea_email_body_contains_plea_and_count_ids(self):
        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "cvxcvx89",
                                 "number_of_charges": 2},
                        "your_details": {"name": "vcx", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx",
                                         "email": "test@test.com"},
                        "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"},
                                               {"mitigations": "test2", "guilty": "guilty"}],
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
                                 "urn": "cvxcvx89",
                                 "number_of_charges": 2},
                        "your_details": {"name": "vcx", "email": "lyndon@antlyn.com", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx"},
                        "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"},
                                               {"mitigations": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data, send_user_email=True)

        self.assertEqual(len(mail.outbox), 3)
        self.assertIn(context_data['case']['urn'].upper(), mail.outbox[-1].body)
        self.assertIn(context_data['your_details']['email'], mail.outbox[-1].to)

    def test_user_confirmation_sends_email_opt_out(self):
        context_data = {"case": {"date_of_hearing": "2014-06-30",
                                 "time_of_hearing": "12:00:00",
                                 "urn": "cvxcvx89",
                                 "number_of_charges": 2},
                        "your_details": {"name": "vcx", "email": "lyndon@antlyn.com", "national_insurance_number": "xxx",
                                         "driving_licence_number": "xxx", "registration_number": "xxx"},
                        "plea": {"PleaForms": [{"mitigations": "test1", "guilty": "guilty"},
                                               {"mitigations": "test2", "guilty": "guilty"}],
                                 "understand": True}}

        send_plea_email(context_data, send_user_email=False)

        self.assertEqual(len(mail.outbox), 3)