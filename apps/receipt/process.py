import contextlib
import datetime as dt
import re
import sys
import traceback

from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import render_to_string

from apps.plea.models import CourtEmailPlea, CourtEmailCount
from .models import ReceiptLog

import gmail

hmcts_body_re = re.compile("<<makeaplea-ref:\s*(\d+)/(\d+)>>")
hmcts_subject_re = re.compile("^Receipt \((Failed|Passed)\) RE:(?:.*?)ONLINE PLEA: (\d{2}/\w{2}/\d{5,7}/\d{2}) DOH: (\d{4}-\d{2}-\d{2})")


class InvalidFormatError(Exception):
    """
    An exception to indicate that we weren't able to parse
    the incoming data
    """


@contextlib.contextmanager
def get_receipt_emails(query_from):
    """
    Retrieve emails from gmail
    """
    g = gmail.login(settings.RECEIPT_INBOX_USERNAME, settings.RECEIPT_INBOX_PASSWORD)

    emails = g.inbox().mail(after=query_from, sender=settings.RECEIPT_INBOX_FROM_EMAIL) #, before=xxx, unread=True, )

    yield emails

    g.logout()


def extract_data_from_email(email):
    """
    Extract data from a HMCTS/GMP receipt email
    """

    matches = hmcts_subject_re.search(email.subject)

    try:
        status, urn, doh = matches.groups()
    except AttributeError:
        raise InvalidFormatError(
            "Cannot process email subject: {}".format(email.subject))

    matches = hmcts_body_re.search(email.body)

    try:
        plea_id, count_id = matches.groups()
    except AttributeError:
        raise InvalidFormatError(
            "Cannot get makeaplea ref from email body: {}".format(email.body))

    return int(plea_id), int(count_id), status, urn, doh


def process_receipts(query_from=None):

    start_time = dt.datetime.now()

    log_entry = ReceiptLog(query_to=start_time)

    try:
        last_log = ReceiptLog.objects.filter(
            status=ReceiptLog.STATUS_COMPLETE).latest('query_to')
    except ReceiptLog.DoesNotExist:
        last_log = None

    # determine the query from date
    if not query_from:
        if last_log:
            query_from = last_log.query_to
        else:
            query_from = start_time-dt.timedelta(days=5)

    log_entry.query_from = query_from
    log_entry.save()

    try:
        _process_receipts(log_entry)
    except Exception as ex:
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

    with get_receipt_emails(log_entry.query_from) as emails:

        log_entry.total_emails = len(emails)

        for email in emails:

            email.fetch()

            try:
                plea_id, count_id, status, urn, doh = \
                    extract_data_from_email(email)

            except InvalidFormatError as ex:
                status_text.append(unicode(ex))

                log_entry.total_errors += 1

                continue

            try:
                plea_obj = CourtEmailPlea.objects.get(id=plea_id)
            except CourtEmailPlea.DoesNotExist:
                status_text.append('Cannot find CourtEmailPlea(<{}>)'
                                   .format(plea_id))

                log_entry.total_errors += 1

                continue

            try:
                count_obj = CourtEmailCount.objects.get(id=count_id)
            except CourtEmailCount.DoesNotExist:
                status_text.append('Cannot find CourtEmailCount(<{}>)'
                                   .format(count_id))

                log_entry.total_errors += 1

                continue

            if status == "Passed":
                plea_obj.status = "receipt_success"

                log_entry.total_success += 1

                status_text.append('Passed: {}'.format(urn))

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