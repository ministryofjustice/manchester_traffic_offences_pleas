# -*- coding: utf-8 -*-
from __future__ import absolute_import
from copy import deepcopy
import re

from django.test import TestCase
from django.core import mail

from apps.plea.attachment import TemplateAttachmentEmail

from ..email import send_plea_email
from ..gov_notify import GovNotify
from ..models import Case, CourtEmailCount, Court, OUCode
from ..standardisers import format_for_region


class EmailGenerationTests(TestCase):

    def setUp(self):
        mail.outbox = []

        self.court_obj = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="Test Magistrates' Court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            test_mode=False)

        OUCode.objects.create(court=self.court_obj, ou_code="B01CN")

        self.test_data_defendant = {"notice_type": {"sjp": False},
                                    "case": {"urn": "06XX0000000",
                                             "date_of_hearing": "2014-06-30",
                                             "contact_deadline": "2014-06-30",
                                             "number_of_charges": 2,
                                             "plea_made_by": "Defendant"},
                                    "your_details": {"updated_address": "Some place",
                                                     "first_name": "v",
                                                     "middle_name": "",
                                                     "last_name": "cx",
                                                     "contact_number": "07000000000",
                                                     "date_of_birth": "1970-01-01",
                                                     "email": "user@example.org"},
                                    "plea": {"data": [{"guilty": "guilty_no_court", "guilty_extra": "test1"},
                                                       {"guilty": "guilty_no_court", "guilty_extra": "test2"}]},
                                    "review": {"understand": True}}

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
                                                      "contact_number": "0800 SOMECOMPANY",
                                                      "email": "company@example.org"},
                                  "plea": {"data": [{"guilty": "guilty_no_court", "guilty_extra": "test1"},
                                                     {"guilty": "guilty_no_court", "guilty_extra": "test2"}]},
                                  "review": {"understand": True}}

        self.gov_notify_client = GovNotify(
            email_address='test_to@example.org',
            personalisation={},
            template_id='d91127f7-814c-4b03-a1fd-10fd5630a49b'
        )

    def test_template_attachment_sends_email(self):
        email_context = {"case": {"urn": "062B3C4D5E"}}
        self.gov_notify_client.personalisation = {
            "subject": "Subject line",
            "email_body": "Body Text"
        }
        self.gov_notify_client.upload_file_link(email_context, "emails/attachments/plea_email.html")

        response = self.gov_notify_client.send_email()

        self.assertEqual(response['content']['subject'], "Subject line")
        self.assertEqual(response['content']['body'], "Body Text")

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

    def test_send_plea_email_with_unicode(self):
        data = deepcopy(self.test_data_defendant)
        data["your_details"]["first_name"] = u"Nørbert"
        data["your_details"]["last_name"] = u"W\\xd3JTOWICZ"

        send_plea_email(data)

    def test_user_confirmation_sends_email(self):
        send_plea_email(self.test_data_defendant)

        self.assertEqual(len(mail.outbox), 3)
        self.assertIn(format_for_region(self.test_data_defendant['case']['urn']), mail.outbox[-1].body)
        self.assertIn(format_for_region(self.test_data_defendant['case']['urn']), mail.outbox[-1].alternatives[0][0])
        self.assertIn(self.test_data_defendant['your_details']['email'], mail.outbox[-1].to)

    def test_user_confirmation_sends_no_email(self):
        self.test_data_defendant['your_details']['email'] = ''

        send_plea_email(self.test_data_defendant)

        self.assertEqual(len(mail.outbox), 2)

    def test_user_confirmation_for_company_uses_correct_email_address(self):
        send_plea_email(self.test_data_company)

        self.assertEqual(len(mail.outbox), 3)
        self.assertIn(format_for_region(self.test_data_company['case']['urn']), mail.outbox[-1].body)
        self.assertIn(format_for_region(self.test_data_company['case']['urn']), mail.outbox[-1].alternatives[0][0])
        self.assertIn(self.test_data_company['company_details']['email'], mail.outbox[-1].to)

    def test_user_confirmation_displays_court_details(self):
        send_plea_email(self.test_data_defendant)

        self.assertIn(self.court_obj.court_name, mail.outbox[-1].body)
        self.assertIn(self.court_obj.court_name, mail.outbox[-1].alternatives[0][0])
        self.assertIn(self.court_obj.court_email, mail.outbox[-1].body)
        self.assertIn(self.court_obj.court_email, mail.outbox[-1].alternatives[0][0])

    def test_sjp_user_confirmation_displays_court_details(self):
        self.test_data_defendant.update({"notice_type": {"sjp": True}})

        send_plea_email(self.test_data_defendant)

        self.assertIn(self.court_obj.court_name, mail.outbox[-1].body)
        self.assertIn(self.court_obj.court_name, mail.outbox[-1].alternatives[0][0])
        self.assertIn(self.court_obj.court_email, mail.outbox[-1].body)
        self.assertIn(self.court_obj.court_email, mail.outbox[-1].alternatives[0][0])

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

    def test_ou_code_email_routing_with_associated_case_no_ou_code(self):
        Case.objects.create(
            urn=self.test_data_defendant["case"]["urn"],
            case_number="xxxxxxx",
            imported=True,
            ou_code="B01LY06")

        self.test_data_defendant["dx"] = True

        send_plea_email(self.test_data_defendant)

        to_emails = [item.to[0] for item in mail.outbox]

        self.assertIn(self.court_obj.submission_email, to_emails)

    def test_ou_code_email_routing_with_associated_case_and_matching_ou_code(self):
        """
        If we have two courts with the same region code, e.g. Lavender Hill and
        Bromley both have URNs that start with 21, then we should be
        sending emails to the correct court based on ou code that is provided in the
        incoming libra data
        """
        Case.objects.create(
            urn=self.test_data_defendant["case"]["urn"],
            case_number="xxxxxxx",
            imported=True,
            ou_code="B01LY01")

        court2 = Court.objects.get(pk=self.court_obj.id)
        court2.id = None
        court2.submission_email = "court2@court.com"
        court2.save()

        OUCode.objects.create(court=court2, ou_code="B01LY")

        self.test_data_defendant["dx"] = True

        send_plea_email(self.test_data_defendant)

        to_emails = [item.to[0] for item in mail.outbox]

        self.assertIn(court2.submission_email, to_emails)
        self.assertNotIn(self.court_obj.submission_email, to_emails)

    def test_ou_code_email_routing_with_no_case(self):
        """
        If we have an ou code for a case and that doesn't match any courts
        then we fall back to matching on region code
        """
        Case.objects.create(
            urn="78xx0000000",
            case_number="xxxxxxx",
            imported=True,
            ou_code="B01LY02")

        court2 = Court.objects.get(pk=self.court_obj.id)
        court2.id = None
        court2.region_code = "01"
        court2.submission_email = "court2@court.com"
        court2.save()

        OUCode.objects.create(court=court2, ou_code="B01LY")

        self.test_data_defendant["dx"] = True

        send_plea_email(self.test_data_defendant)

        to_emails = [item.to[0] for item in mail.outbox]

        self.assertIn(self.court_obj.submission_email, to_emails)
        self.assertNotIn(court2.submission_email, to_emails)

