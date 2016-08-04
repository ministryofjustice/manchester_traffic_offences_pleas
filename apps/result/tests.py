# -*- coding: utf8 -*-

import datetime as dt
from decimal import Decimal
from cStringIO import StringIO

from django.core import mail
from django.test import TestCase

from apps.plea.models import Court, Case, CaseOffenceFilter
from .models import Result, ResultOffenceData, ResultOffence
from .management.commands.process_results import Command


class ResultTestCase(TestCase):

    def setUp(self):
        self.test_court = Court.objects.create(
            court_code="1234",
            region_code="51",
            court_name="Test Court",
            enabled=True
        )

        self.test_case1 = Case.objects.create(
            case_number="12345678",
            urn="51XX0000000",
            email="test@test123.com",
            sent=True
        )

        self.test_result1 = Result.objects.create(
            urn="51XX0000000",
            case_number="12345678",
            date_of_hearing=dt.date.today(),
            sent=False,
            processed=False,
            account_number="12345",
            division="100"
        )

        self.offence1 = ResultOffence.objects.create(
            result=self.test_result1,
            offence_code="XXXXXXX",
            offence_seq_number="001"
        )

        self.offence2 = ResultOffence.objects.create(
            result=self.test_result1,
            offence_code="YYYYYYY",
            offence_seq_number="002"
        )

        self.f_code_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="FCOST",
            result_short_title="FINAL CODE"
        )

    def test_has_valid_offences_with_non_whitelisted_offences(self):

        CaseOffenceFilter.objects.create(filter_match="VVVVV", description="A test whitelist entry")

        self.assertFalse(self.test_result1.has_valid_offences())

    def test_has_valid_offences_with_all_whitelisted_offences(self):

        CaseOffenceFilter.objects.create(filter_match="YYYYY", description="A test whitelist entry")
        CaseOffenceFilter.objects.create(filter_match="XXXX", description="A test whitelist entry")

        self.assertTrue(self.test_result1.has_valid_offences())

    def test_can_result_succeeds(self):

        result, _ = self.test_result1.can_result()

        self.assertTrue(result)

    def test_can_result_no_welsh(self):

        self.test_case1.language = "cy"
        self.test_case1.save()

        result, _ = self.test_result1.can_result()

        self.assertFalse(result)

    def test_can_result_with_adjourned_offence_is_false(self):

        self.f_code_offence.delete()

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="A",
            result_short_title="ADJOURNED!"
        )

        result, _ = self.test_result1.can_result()

        self.assertFalse(result)

    def test_can_result_with_adjourned_and_withdrawn_offence_is_true(self):

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="A",
            result_short_title="ADJOURNED!"
        )

        self.withdrawn_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="WDRN",
            result_short_title="FINE VICTIM SURCHARGE!"
        )

        result, _ = self.test_result1.can_result()

        self.assertTrue(result)

    def test_can_result_with_adjourned_and_final_codes_is_true(self):

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="A",
            result_short_title="ADJOURNED!"
        )

        self.withdrawn_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="WDRN",
            result_short_title="WITHDRAWN!"
        )

    def test_can_result_with_disqualified_code_is_false(self):

        self.withdrawn_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="DDDT",
            result_short_title="DISQUALIFIED!"
        )

        result, _ = self.test_result1.can_result()

        self.assertFalse(result)

    def test_can_result_missing_divcode_or_acc_number(self):
        self.test_result1.account_number = ""
        self.test_result1.save()

        result, _ = self.test_result1.can_result()

        self.assertFalse(result)

        self.test_result1.account_number = "12345"
        self.test_result1.division = ""
        self.test_result1.save()

        result, _ = self.test_result1.can_result()

        self.assertFalse(result)

    def test_get_offence_totals_fines(self):

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="FCOST",
            result_short_title="FINE"
        )

        fines, _, _ = self.test_result1.get_offence_totals()

        self.assertEquals(len(fines), 2)

    def test_get_offence_totals_endorsements(self):

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="LEP",
            result_short_title="ENDORSEMENT"
        )

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence2,
            result_code="LEP",
            result_short_title="ENDORSEMENT"
        )

        _, endorsements, _ = self.test_result1.get_offence_totals()

        self.assertEquals(len(endorsements), 2)

    def test_get_offence_totals_total(self):

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="FCOST",
            result_short_title="FINE",
            result_wording=u"asdfsadf £75.00 asasdfadfs"
        )

        self.adjourned_offence = ResultOffenceData.objects.create(
            result_offence=self.offence2,
            result_code="FVS",
            result_short_title="FINE",
            result_wording=u"asdfsadf £25.00 asasdfadfs"
        )

        _, _, total = self.test_result1.get_offence_totals()

        self.assertEquals(Decimal("100"), total)


class ProcessResultsTestCase(TestCase):

    def setUp(self):

        self.test_court = Court.objects.create(
            court_code="1234",
            region_code="51",
            court_name="Test Court",
            enabled=True,
        )

        self.test_case1 = Case.objects.create(
            case_number="12345678",
            urn="51XX0000000",
            sent=True,
            email="frank.marsh@marshtech.com"
        )

        self.test_result1 = Result.objects.create(
            urn="51XX0000000",
            case_number="12345678",
            date_of_hearing=dt.date.today(),
            sent=False,
            processed=False,
            account_number="12345",
            division="100"
        )

        self.offence1 = ResultOffence.objects.create(
            result=self.test_result1
        )

        self.adjourned_result = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="A",
            result_short_title="ADJOURNED"
        )

        self.withdrawn_result = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="WDRN",
            result_short_title="WITHDRAWN"
        )

        self.final_result = ResultOffenceData.objects.create(
            result_offence=self.offence1,
            result_code="FCOST",
            result_short_title="FINAL"
        )

        self.command = Command(stdout=StringIO())

        self.opts = dict(
            override_recipient="",
            status_email_recipients="",
            dry_run=False,
            date="")

    def test_matching_case_with_email_is_sent(self):

        self.command.handle(**self.opts)

        result = Result.objects.get(pk=self.test_result1.id)
        self.assertTrue(result.sent)
        self.assertTrue(result.processed)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [self.test_case1.email])

    def test_option_override_recipient(self):

        self.opts["override_recipient"] = "override@xyzyzyz.com"

        self.command.handle(**self.opts)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, ["override@xyzyzyz.com"])

    def test_option_dry_run(self):

        self.opts["dry_run"] = True
        self.command.handle(**self.opts)

        result = Result.objects.get(pk=self.test_result1.id)
        self.assertFalse(result.processed)
        self.assertFalse(result.sent)

    def test_option_send_status_email(self):

        self.opts["dry_run"] = True
        self.opts["status_email_recipients"] = "statusemail@testxyz.com"

        self.command.handle(**self.opts)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, ["statusemail@testxyz.com"])

    def test_no_supplied_email_no_result(self):

        self.test_case1.email = None
        self.test_case1.save()

        self.command.handle(**self.opts)

        result = Result.objects.get(pk=self.test_result1.id)
        self.assertTrue(result.processed)
        self.assertFalse(result.sent)

    def test_no_matching_case_no_email(self):

        self.test_case1.delete()
        self.command.handle(**self.opts)

        result = Result.objects.get(pk=self.test_result1.id)

        self.assertTrue(result.processed)
        self.assertFalse(result.sent)

    def test_case_not_sent_result_not_sent(self):
        """
        If the case does not have sent=True, do not send the result email
        """

        self.test_case1.sent = False
        self.test_case1.save()

        self.command.handle(**self.opts)

        result = Result.objects.get(id=self.test_result1.id)

        self.assertFalse(result.sent)
        self.assertTrue(result.processed)

    def test_result_sent_not_resent(self):

        self.test_result1.sent = True
        self.test_result1.save()

        self.command.handle(**self.opts)

        result = Result.objects.get(pk=self.test_result1.id)

        self.assertEquals(mail.outbox, [])

    def test_result_is_marked_sent_and_processed(self):
        assert not self.test_result1.sent

        self.command.handle(**self.opts)

        result = Result.objects.get(pk=self.test_result1.id)

        self.assertTrue(result.sent)
        self.assertTrue(result.processed)

    def test_date_option(self):

        assert self.test_result1.created.date() == dt.date.today()

        self.opts["date"] = (dt.date.today()-dt.timedelta(7)).strftime("%d/%m/%Y")

        self.command.handle(**self.opts)

        result = Result.objects.get(pk=self.test_result1.id)

        self.assertFalse(result.sent)
        self.assertFalse(result.processed)


