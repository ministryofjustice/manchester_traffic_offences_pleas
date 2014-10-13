from django.test import TestCase

from mock import MagicMock, patch

from apps.receipt.process import get_status_from_subject, InvalidFormatError


class TestEmailSubjectProcessing(TestCase):

    def setUp(self):
        self.passed_email_subject = "Receipt (Passed) RE: FILED! ONLINE PLEA: 06/xa/0051925/14 DOH: 2014-10-31 XXXXXX xxxxx"
        self.failed_email_subject = "Receipt (Failed) RE: ONLINE PLEA: 66/XX/0050782/14 DOH: 2014-11-07 XXXXXX Xxxxxx"

    def test_failed_match(self):
        status, urn, doh = get_status_from_subject(self.passed_email_subject)

        self.assertEquals(status, "Passed")

    def test_passed_match(self):
        status, urn, doh = get_status_from_subject(self.failed_email_subject)

        self.assertEquals(status, "Failed")

    def test_error_match(self):

        with self.assertRaises(InvalidFormatError):
            get_status_from_subject('a totally invalid email subject')


class TestProcessReceipts(TestCase):

    def setUp(self):
        pass

    def test_gmail_exception_is_logged(self):
        pass

    def test_success_responses_are_recorded(self):
        pass

    def test_failed_responses_are_recorded(self):
        pass

    def test_invalid_email_subjects_are_ignored(self):
        pass