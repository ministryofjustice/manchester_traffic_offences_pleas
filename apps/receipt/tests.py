import datetime as dt
import json

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings

from mock import Mock, patch

from apps.plea.models import CourtEmailCount, Case
from .models import ReceiptLog
from .process import (extract_data_from_email, InvalidFormatError,
                                  process_receipts)
from .views import ReceiptWebhook
from apps.plea.models import Court


class TestEmailSubjectProcessing(TestCase):

    def setUp(self):

        self.failed_email_subject = "Receipt (Failed) RE: ONLINE PLEA: 66/XX/0050782/14 DOH: 2014-11-07 XXXXXX Xxxxxx"
        self.passed_email_subject = "Receipt (Passed) RE: FILED! ONLINE PLEA: 06/xa/0051925/14 DOH: 2014-10-31 XXXXXX xxxxx"

        self.email_body_valid = """
        Random content.
        <<<makeaplea-ref: 1/1>>>
        Random content.
        """

    def test_failed_match(self):

        plea_id, count_id, status, urn, doh = \
            extract_data_from_email(self.failed_email_subject,
                                    self.email_body_valid)

        self.assertEqual(status, "Failed")

    def test_passed_match(self):

        plea_id, count_id, status, urn, doh = \
            extract_data_from_email(self.passed_email_subject,
                                    self.email_body_valid)

        self.assertEqual(status, "Passed")

    def test_error_match(self):

        with self.assertRaises(InvalidFormatError):
            extract_data_from_email('a totally invalid email subject',
                                    self.email_body_valid)

    def test_email_body_valid(self):
        plea_id, count_id, status, urn, doh = \
            extract_data_from_email(self.passed_email_subject,
                                    self.email_body_valid)

        self.assertEqual(plea_id, 1)
        self.assertEqual(count_id, 1)

    def test_email_body_invaild(self):

        with self.assertRaises(InvalidFormatError):
            extract_data_from_email(self.passed_email_subject,
                                    "This is an invalid body")


class TestProcessReceipts(TestCase):

    def setUp(self):
        mail.outbox = []

        self.urn = "00/AA/0000000/00"
        self.doh = dt.datetime.now()+dt.timedelta(5)

        context_data = {
            'case': {
                'urn': self.urn
            }
        }

        self.case = Case.objects.create(
            urn=self.urn,
            sent=True,
            processed=False)

        self.court = Court.objects.create(
            court_code="51",
            region_code="06",
            court_name="whatever",
            court_address="asdf",
            enabled=True,
            court_telephone="00000",
            court_email="court@example.org",
            submission_email="",
            court_receipt_email="sending@example.org",
            local_receipt_email="incoming@example.org",
            test_mode=False)

        self.email_count = CourtEmailCount.objects.create(
            court=self.court,
            hearing_date=self.doh,
            total_pleas=1,
            total_guilty=1,
            total_not_guilty=0,
            sent=True,
            processed=False)

        patcher = patch('apps.receipt.process.get_receipt_emails')
        self.addCleanup(patcher.stop)
        self.get_emails_mock = patcher.start()

    def _get_email_mock(self, body, subject):

        email = Mock()
        email.body = body
        email.subject = subject

        return email

    def _get_context_mock(self, **kwargs):
        """
        Mock the get_receipt_emails context manager
        """

        inner_mock = Mock()
        inner_mock.__enter__ = Mock(**kwargs)
        inner_mock.__exit__ = Mock(return_value=False)

        return inner_mock

    def test_exception_is_logged(self):

        email_obj_mock = Mock()
        email_obj_mock.fetch = Mock(side_effect=IOError("Broken"))

        self.get_emails_mock.return_value = \
            self._get_context_mock(return_value=[email_obj_mock])

        process_receipts()

        self.assertEqual(ReceiptLog.objects.all().count(), 1)
        log = ReceiptLog.objects.latest('id')

        self.assertEqual(log.status, ReceiptLog.STATUS_ERROR)
        self.assertIn('Broken', log.status_detail)

    def test_success_responses_are_recorded(self):

        ref = "<<<makeaplea-ref: {}/{}>>>"\
            .format(self.case.id, self.email_count.id)

        subject = "Receipt (Passed) RE: FILED! ONLINE PLEA: {} DOH: {}"\
            .format(self.urn, self.doh.strftime("%G-%m-%d"))

        email_obj_mock = self._get_email_mock(ref, subject)

        self.get_emails_mock.return_value = \
        self._get_context_mock(return_value=[email_obj_mock])

        process_receipts()

        case_obj = Case.objects.get(pk=self.case.id)
        count_obj = CourtEmailCount.objects.get(pk=self.email_count.id)

        self.assertTrue(case_obj.processed)

        self.assertTrue(case_obj.has_action("receipt_success"))
        self.assertEquals(case_obj.sent, count_obj.sent)
        self.assertEquals(case_obj.processed, count_obj.processed)

        self.assertEqual(ReceiptLog.objects.all().count(), 1)
        log = ReceiptLog.objects.latest('id')
        self.assertEqual(log.total_success, 1)
        self.assertEqual(log.total_emails, 1)
        self.assertEqual(log.total_failed, 0)

    def test_failed_responses_are_recorded(self):
        ref = "<<<makeaplea-ref: {}/{}>>>"\
            .format(self.case.id, self.email_count.id)

        subject = "Receipt (Failed) RE: ONLINE PLEA: {} DOH: {}"\
            .format(self.urn, self.doh.strftime("%G-%m-%d"))

        email_obj_mock = self._get_email_mock(ref, subject)

        self.get_emails_mock.return_value = \
        self._get_context_mock(return_value=[email_obj_mock])

        process_receipts()

        case_obj = Case.objects.get(pk=self.case.id)
        count_obj = CourtEmailCount.objects.get(pk=self.email_count.id)

        self.assertTrue(case_obj.has_action("receipt_failure"))
        self.assertEquals(case_obj.sent, count_obj.sent)
        self.assertEquals(case_obj.processed, count_obj.processed)

        self.assertEqual(ReceiptLog.objects.all().count(), 1)
        log = ReceiptLog.objects.latest('id')
        self.assertEqual(log.total_emails, 1)
        self.assertEqual(log.total_success, 0)
        self.assertEqual(log.total_failed, 1)

    def test_mismatched_ref_id(self):
        ref = "<<<makeaplea-ref: {}/{}>>>"\
            .format(self.case.id, self.email_count.id+1)

        subject = "Receipt (Failed) RE: ONLINE PLEA: {} DOH: {}"\
            .format(self.urn, self.doh.strftime("%G-%m-%d"))

        email_obj_mock = self._get_email_mock(ref, subject)

        self.get_emails_mock.return_value = \
        self._get_context_mock(return_value=[email_obj_mock])

        process_receipts()

        log = ReceiptLog.objects.latest('id')

        self.assertEqual(log.total_emails, 1)
        self.assertEqual(log.total_failed, 0)
        self.assertEqual(log.total_errors, 1)

    def test_invalid_email_subjects_are_ignored_but_logged(self):
        ref = "<<<makeaplea-ref: {}/{}>>>"\
            .format(self.case.id, self.email_count.id+1)

        subject = "gibberish"

        email_obj_mock = self._get_email_mock(ref, subject)

        self.get_emails_mock.return_value = \
        self._get_context_mock(return_value=[email_obj_mock])

        process_receipts()

        log = ReceiptLog.objects.latest('id')
        self.assertEqual(log.total_emails, 1)
        self.assertEqual(log.total_failed, 0)
        self.assertEqual(log.total_errors, 1)

    def test_records_changed_on_changed_urn(self):

        updated_urn = "06/BB/0000000/00"

        ref = "<<<makeaplea-ref: {}/{}>>>"\
            .format(self.case.id, self.email_count.id)

        subject = "Receipt (Passed) RE: FILED! ONLINE PLEA: {} DOH: {}"\
            .format(updated_urn, self.doh.strftime("%G-%m-%d"))

        email_obj_mock = self._get_email_mock(ref, subject)

        self.get_emails_mock.return_value = \
        self._get_context_mock(return_value=[email_obj_mock])

        process_receipts()

        case_obj = Case.objects.get(pk=self.case.id)
        count_obj = CourtEmailCount.objects.get(pk=self.email_count.id)

        self.assertTrue(case_obj.has_action("receipt_success"))
        self.assertEquals(case_obj.sent, count_obj.sent)
        self.assertEquals(case_obj.processed, count_obj.processed)

        log = ReceiptLog.objects.latest('id')
        self.assertEqual(log.total_emails, 1)
        self.assertEqual(log.total_success, 1)

        case = Case.objects.get(pk=self.case.id)

        self.assertEqual(case.urn, updated_urn)

        action = case.actions.latest()
        self.assertIn(self.urn, action.status_info)
        self.assertIn("URN CHANGED!", action.status_info)

    def test_monitoring_email_is_sent_when_enabled(self):

        self.get_emails_mock.return_value = \
        self._get_context_mock(return_value=[])

        with self.settings(RECEIPT_ADMIN_EMAIL_ENABLED=True):
            process_receipts()

        self.assertEqual(len(mail.outbox), 1)


class WebHookTestCase(TestCase):
    def setUp(self):

        self.factory = RequestFactory()

        self.failed_email_subject = "Receipt (Failed) RE: ONLINE PLEA: 66/XX/0050782/14 DOH: 2014-11-07 XXXXXX Xxxxxx"
        self.passed_email_subject = "Receipt (Passed) RE: FILED! ONLINE PLEA: 06/xa/0051925/14 DOH: 2014-10-31 XXXXXX xxxxx"

        self.urn = "00/AA/0000000/00"
        self.doh = dt.datetime.now()+dt.timedelta(5)

        self.case = Case.objects.create(
            urn=self.urn,
            sent=True,
            processed=False)

        self.court = Court.objects.create(
            court_code="51",
            region_code="06",
            court_name="whatever",
            court_address="asdf",
            enabled=True,
            court_telephone="00000",
            court_email="court@example.org",
            submission_email="",
            court_receipt_email="sending@example.org",
            local_receipt_email="incoming@example.org",
            test_mode=False)

        self.email_count = CourtEmailCount.objects.create(
            hearing_date=self.doh,
            court=self.court,
            total_pleas=1,
            total_guilty=1,
            total_not_guilty=0,
            sent=True,
            processed=False)

        self.email_body_valid = """
        Random content.
        <<<makeaplea-ref: {}/{}>>>
        Random content.
        """.format(self.case.id, self.email_count.id)

    def _get_mandrill_post_data(self, subject=None, text=None, from_email=None, email=None):
        return {
            "mandrill_events": json.dumps([{
                "msg": {
                    "subject": subject or self.passed_email_subject,
                    "text": text or self.email_body_valid,
                    "from_email": from_email or "sending@example.org",
                    "email": email or "incoming@example.org",
                    "headers": {
                        "Received": [
                            "DKIMwhatever: somerequiredtext"
                        ]
                    }
                }
            }])
        }

    def test_success_entry(self):

        request = self.factory.post(reverse("receipt_webhook"),
                                    self._get_mandrill_post_data())

        ReceiptWebhook.as_view()(request)

        self.assertEquals(CourtEmailCount.objects.all().count(), 1)

        self.assertEquals(ReceiptLog.objects.all().count(), 1)

        log = ReceiptLog.objects.all()[0]

        case = Case.objects.get(pk=self.case.id)

        self.assertEquals(case.processed, True)
        self.assertEquals(log.total_emails, 1)
        self.assertEquals(log.total_success, 1)
        self.assertEquals(log.total_failed, 0)
        self.assertEquals(log.total_errors, 0)

    def test_failed_entry(self):

        request = self.factory.post(reverse("receipt_webhook"),
                                    self._get_mandrill_post_data(
                                        subject=self.failed_email_subject))

        ReceiptWebhook.as_view()(request)

        self.assertEquals(CourtEmailCount.objects.all().count(), 1)

        self.assertEquals(ReceiptLog.objects.all().count(), 1)

        log = ReceiptLog.objects.all()[0]

        self.assertEquals(log.total_emails, 1)
        self.assertEquals(log.total_success, 0)
        self.assertEquals(log.total_failed, 1)
        self.assertEquals(log.total_errors, 0)

    def test_errored_entry(self):

        self.case.delete()

        request = self.factory.post(reverse("receipt_webhook"),
                                    self._get_mandrill_post_data(
                                        subject=self.passed_email_subject))

        ReceiptWebhook.as_view()(request)

        self.assertEquals(ReceiptLog.objects.all().count(), 1)

        log = ReceiptLog.objects.all()[0]

        self.assertEquals(log.total_emails, 1)
        self.assertEquals(log.total_success, 0)
        self.assertEquals(log.total_failed, 0)
        self.assertEquals(log.total_errors, 1)

    @override_settings(RECEIPT_HEADER_FRAGMENT_CHECK="MUSTHAVETHISTEXT")
    def test_missing_header(self):
        request = self.factory.post(reverse("receipt_webhook"),
                                    self._get_mandrill_post_data())

        ReceiptWebhook.as_view()(request)

        self.assertEquals(ReceiptLog.objects.all().count(), 1)

        log = ReceiptLog.objects.all()[0]

        self.assertEquals(log.total_emails, 1)
        self.assertEquals(log.total_success, 0)
        self.assertEquals(log.total_failed, 0)
        self.assertEquals(log.total_errors, 1)

    def test_invalid_emails(self):

        request = self.factory.post(reverse("receipt_webhook"),
                                    self._get_mandrill_post_data(from_email="invalid@invalid.com"))

        ReceiptWebhook.as_view()(request)

        self.assertEquals(ReceiptLog.objects.all().count(), 1)

        log = ReceiptLog.objects.all()[0]

        self.assertEquals(log.total_emails, 1)
        self.assertEquals(log.total_success, 0)
        self.assertEquals(log.total_failed, 0)
        self.assertEquals(log.total_errors, 1)
