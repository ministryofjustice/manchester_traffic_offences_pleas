import datetime
import re

from dateutil.relativedelta import relativedelta
from django.core import exceptions

from .models import Case, Court
from .standardisers import get_standardiser


URN_PATTERNS = {
    "02": r"02TJDS[0-9]{4}/[0-9]{2}/[0-9]{4}[A-Z]{2}",
    "05": r"[0-9]{2}/[A-Z]{1}[0-9]{1}/(?:[0-9]{5}|[0-9]{7})/[0-9]{2}",
    "17": r"[0-9]{2}/[A-Z]{1}[0-9]{1}/(?:[0-9]{5}|[0-9]{7})/[0-9]{2}",
    "*": r"[0-9]{2}/[A-Z]{2}/(?:[0-9]{5}|[0-9]{7})/[0-9]{2}"
}


def get_pattern(urn):
    return URN_PATTERNS.get(urn[:2], URN_PATTERNS["*"])


def is_date_in_past(date):
    if date >= datetime.datetime.today().date():
        raise exceptions.ValidationError("The date must be in the past", code="is_date_in_past")

    return True


def is_date_in_future(date):
    if date <= datetime.datetime.today().date():
        raise exceptions.ValidationError("The date must be in the future", code="is_date_in_future")

    return True


def is_date_in_last_28_days(date):
    if date < datetime.datetime.today().date() + relativedelta(days=-28):
        raise exceptions.ValidationError("The date must be within the last 28 days", code="is_date_in_last_28_days")

    return True


def is_date_in_next_6_months(date):
    if date > datetime.datetime.today().date() + relativedelta(months=+6):
        raise exceptions.ValidationError("The date must be within the next 6 months", code="is_date_in_next_6_months")

    return True


def is_urn_valid(urn):
    """
    URN is 11 or 13 characters long in the following format:

    00/AA/0000000/00
    or
    00/AA/00000/00
    """
    standardise = get_standardiser(urn)
    urn = standardise(urn)
    pattern = get_pattern(urn)

    """
    The validation of URN format and whether URN belongs to a court should really
    be separate. However, supplying separate messages for these 2 validation errors
    could be seen as opening a backdoor for users to try and 'guess' valid URNs.

    This should be reviewed when DX data comes into play.
    """
    if not re.match(pattern, urn) or not Court.objects.has_court(urn):
        raise exceptions.ValidationError("The URN is not valid", code="is_urn_valid")

    court = Court.objects.get_by_urn(urn)
    if court.validate_urn and not Case.objects.filter(urn__iexact=urn, sent=False).exists():
        raise exceptions.ValidationError("The URN is not valid", code="is_urn_valid")

    return True


def is_urn_not_used(urn):
    """
    Check that the urn hasn't already been used in a previous submission
    """

    standardise = get_standardiser(urn)
    urn = standardise(urn)

    if not Case.objects.can_use_urn(urn):
        raise exceptions.ValidationError("The URN has already been used", code="is_urn_not_used")

    return True
