import contextlib
import datetime as dt
import re

from django.conf import settings

from apps.plea.models import CourtEmailPlea
from .models import ReceiptLog

import gmail


gmp_email_re = re.compile("^Receipt \((Failed|Passed)\) RE:(?:.*?)ONLINE PLEA: (\d{2}/\w{2}/\d{7}/\d{2}) DOH: (\d{4}-\d{2}-\d{2})")


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

    emails = g.inbox().mail(after=query_from) #, before=xxx, unread=True, sender=settings.RECEIPT_INBOX_FROM_EMAIL)

    yield emails

    g.logout()


def get_status_from_subject(subject):
    matches = gmp_email_re.search(subject)

    try:
        status, urn, doh = matches.groups()
    except (AttributeError, InvalidFormatError):
        raise InvalidFormatError(
            "Cannot process email subject: {}".format(subject))

    return status, urn, doh


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
        log_entry.status_detail += "\n An exception has occured: {}".format(unicode(ex))
        log_entry.status = ReceiptLog.STATUS_ERROR

    log_entry.run_time = (dt.datetime.now() - start_time).seconds
    log_entry.save()


def _process_receipts(log_entry):

    status_text = []

    with get_receipt_emails(log_entry.query_from) as emails:

        log_entry.total_emails = len(emails)

        for email in emails:

            email.fetch()

            try:
                urn, status, doh = get_status_from_subject(email.subject)
            except InvalidFormatError as ex:
                status_text.append(str(ex))
                log_entry.total_errors += 1

                continue

            try:
                plea_audit = CourtEmailPlea.objects.get(urn=urn.upper())
            except CourtEmailPlea.DoesNotExist:
                status_text.append('Unmatched URN: {} email subject: {}'.format(urn, email.subject))

                log_entry.total_errors += 1

                continue

            # has the plea already been processed?

            if status == "success":
                plea_audit.status = "receipt_success"

                log_entry.total_success += 1

                #
                # do outbound actions, e.g. send an email to a user.
                #

                # mark as read
                email.read()
            else:
                plea_audit.status = "receipt_failure"

                log_entry.total_failed += 1

    log_entry.status = log_entry.STATUS_COMPLETE

    log_entry.status_detail = "\n".join(status_text)




