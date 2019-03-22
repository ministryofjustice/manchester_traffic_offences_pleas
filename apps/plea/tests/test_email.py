from django.test import TestCase
from ..tasks import get_smtp_gateway


class EmailTests(TestCase):
    def test_public_smtp_gataway_returned_for_non_gsi_emails(self):
        self.assertEquals(get_smtp_gateway('test@hmcts.gsi.gov.uk'), 'GSI')
        self.assertEquals(get_smtp_gateway('test@justice.gov.uk'), 'PUB')
        self.assertEquals(get_smtp_gateway('test@hmcts.net'), 'PUB')
