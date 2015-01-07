import contextlib
import datetime as dt
import re
import sys
import traceback

from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import render_to_string

from apps.plea.models import CourtEmailCount, Case
from .models import ReceiptLog

import gmail

hmcts_body_re = re.compile("<<<makeaplea-ref:\s*(\d+)/(\d+)>>>")
hmcts_subject_re = re.compile("(?:.*?)Receipt \((Failed|Passed)\) RE:(?:.*?)ONLINE PLEA: (\d{2}/\w{2}/\d{5,7}/\d{2}) DOH:\s+(\d{4}-\d{2}-\d{2})")


class InvalidFormatError(Exception):
    """
    Unable to parse the incoming email data
    """


@contextlib.contextmanager
def get_receipt_emails(query_from, query_to):
    """
    Retrieve emails from gmail
    """
    g = gmail.login(settings.RECEIPT_INBOX_USERNAME, settings.RECEIPT_INBOX_PASSWORD)

    # NOTE: the query_from/query_to has been removed.  This script will only
    # try to process emails that are unread and it'll set them to read after
    # being processed Maybe later on we need to start querying date ranges,
    # but given the volume of emails this should be a more robust solution.

    emails = g.inbox().mail(sender=settings.RECEIPT_INBOX_FROM_EMAIL, unread=True)

    yield emails

    g.logout()


def extract_data_from_email(email):
    """
    Extract data from a HMCTS/GMP receipt email
    """

    matches = hmcts_subject_re.search(email.subject)

    if not matches:
        raise InvalidFormatError(
            "Cannot process email subject: {}".format(email.subject))
    else:
        status, urn, doh = matches.groups()

    matches = hmcts_body_re.search(email.body)

    if not matches:
        raise InvalidFormatError(
            "Cannot get makeaplea ref from email body: {} / {} / {}"
            .format(status, urn, doh))
    else:
        plea_id, count_id = matches.groups()

    return int(plea_id), int(count_id), status, urn, doh


def process_receipts(query_from=None):
    """
    Retrieve HMCTS receipt emails from google mail, process them and log the
    results.

    HMCTS will respond with either a Passed or Failed status, as per the email
    subject).

    A Failed status means HMCTS have been unable to match a submission with
    existing Libra court records.

    Several Failed emails may be received before a final Passed status,
    e.g when HMCTS staff finally determine the correct court records for
    the submission.

    However, sometimes a submission will not be matched in which case we'll
    receive a Failed status from HMCTS with no subsequent Passed status.

    If a submission is failed, due to an incorrect hearing date or URN,
    then HMCTS may manually correct the URN or hearing date and respond
    with a Passed status.

    In this instance we pick up the corrected hearing date and/or DOH,
    and update our own records whilst recording that a URN or DOH change
    has been made.

    To associate outbound email submissions with our own records we
    insert the relevant IDs into the body of the outbound email in the
    following format:

    <<<makeaplea-ref: {CaseId}, {CourtEmailCountId}>>>

    HMCTS receipt emails include the reference enabling us to
    know which Case and CourtEmailCount data needs
    to be modified.

    This function is run as a management command:

    ./manage.py process_receipt_emails

    """

    start_time = dt.datetime.now()

    try:
        last_log = ReceiptLog.objects.filter(
            status=ReceiptLog.STATUS_COMPLETE).latest('query_to')
    except ReceiptLog.DoesNotExist:
        last_log = None

    log_entry = ReceiptLog(query_to=start_time)

    # determine the query from date
    if not query_from:
        if last_log:
            query_from = last_log.query_to
        else:
            query_from = start_time-dt.timedelta(days=1)

    log_entry.query_from = query_from
    log_entry.save()

    try:
        _process_receipts(log_entry)
    except Exception:
        ex_type, ex, tb = sys.exc_info()
        log_entry.status_detail = "An exception has occured: {}\n\n{}"\
            .format(ex, traceback.format_tb(tb))
        log_entry.status = ReceiptLog.STATUS_ERROR

    log_entry.run_time = (dt.datetime.now() - start_time).seconds
    log_entry.save()

    if settings.RECEIPT_ADMIN_EMAIL_ENABLED:
        body = render_to_string('email/admin_receipt_email.txt', {'log': log_entry})
        mail_admins(settings.RECEIPT_ADMIN_EMAIL_SUBJECT, body)

    return log_entry


def _process_receipts(log_entry):

    status_text = []

    with get_receipt_emails(log_entry.query_from, log_entry.query_to) as emails:

        log_entry.total_emails = len(emails)

        for email in emails:

            email.fetch()

            try:
                plea_id, count_id, status, urn, doh = \
                    extract_data_from_email(email)

            except InvalidFormatError as ex:
                status_text.append(unicode(ex))

                log_entry.total_errors += 1

                email.read()
                email.star()

                continue

            try:
                plea_obj = Case.objects.get(id=plea_id)
            except Case.DoesNotExist:
                status_text.append('Cannot find Case(<{}>)'
                                   .format(plea_id))

                log_entry.total_errors += 1

                email.read()
                email.star()

                continue

            try:
                count_obj = CourtEmailCount.objects.get(id=count_id)
            except CourtEmailCount.DoesNotExist:
                status_text.append('Cannot find CourtEmailCount(<{}>)'
                                   .format(count_id))

                log_entry.total_errors += 1

                email.read()
                email.star()

                continue

            if status == "Passed":
                if plea_obj.status == "receipt_success":
                    status_text.append("{} already processed. Skipping.").format(urn)
                    continue

                plea_obj.status = "receipt_success"

                log_entry.total_success += 1

                if urn.upper() != plea_obj.urn:
                    # HMCTS have changed the URN, update our records and log the change

                    old_urn, plea_obj.urn = plea_obj.urn, urn

                    plea_obj.status_info = \
                        (plea_obj.status_info or "") +\
                        "\nURN CHANGED! Old Urn: {}".format(old_urn)

                    plea_obj.save()

                    count_obj.get_from_context(data)
                    count_obj.save()

                    status_text.append('Passed [URN CHANGED! old urn: {}] {}'.format(urn, old_urn))
                else:
                    status_text.append('Passed: {}'.format(urn))

                # We can't modify the DOH as the hearing time is not provided by
                # hmcts, at current

                #
                # do outbound actions, e.g. send an email to a user.
                #

            else:
                plea_obj.status = "receipt_failure"

                status_text.append('Failed: {}'.format(urn))

                log_entry.total_failed += 1

            # mark as read
            email.read()

    log_entry.status = log_entry.STATUS_COMPLETE

    log_entry.status_detail = "\n".join(status_text)
