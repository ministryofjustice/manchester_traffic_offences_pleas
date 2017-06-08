import datetime
import re

from dateutil.relativedelta import relativedelta
from django.core import exceptions

from .models import AuditEvent, Case, Court
from .standardisers import standardise_urn, StandardiserNoOutputException


UNFORMATTED_URN_PATTERNS = {
    "02": r"^02TJ[A-Z]{0,2}[0-9]{6,18}[A-Z]{2,5}$",
    "05": r"^[0-9]{2}[A-Z]{1}[0-9]{1}(?:[0-9]{5}|[0-9]{7})[0-9]{2}$",
    "10": r"^[0-9]{2}[A-Z]{1}[0-9]{1}(?:[0-9]{5}|[0-9]{7})[0-9]{2}$",
    "17": r"^[0-9]{2}[A-Z]{1}[0-9]{1}(?:[0-9]{5}|[0-9]{7})[0-9]{2}$",
    "20": r"^[0-9]{2}[A-Z]{1}[A-Z0-9]{1}(?:[0-9]{5}|[0-9]{7})[0-9]{2}$",
    "32": r"^[0-9]{2}[A-Z]{1}[0-9]{6}[0-9]{2}$",
    "41": r"^[0-9]{2}[A-Z]{1}[0-9]{6}[0-9]{2}$",
    "*": r"^[0-9]{2}[A-Z]{2}(?:[0-9]{5}|[0-9]{7})[0-9]{2}$"
}


def get_pattern(urn):
    return UNFORMATTED_URN_PATTERNS.get(urn[:2], UNFORMATTED_URN_PATTERNS["*"])


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
        raise exceptions.ValidationError(
            "The date must be within the last 28 days",
            code="is_date_in_last_28_days")

    return True


def is_date_in_next_6_months(date):
    if date > datetime.datetime.today().date() + relativedelta(months=+6):
        raise exceptions.ValidationError(
            "The date must be within the next 6 months",
            code="is_date_in_next_6_months")

    return True


def is_urn_valid(urn):
    try:
        urn = standardise_urn(urn)
    except StandardiserNoOutputException:
        AuditEvent().populate(
            event_type="urn_validator",
            event_subtype="case_invalid_invalid_urn",
            event_trace="'is_urn_valid' raised StandardiserNoOutputException with URN {0}.format(urn)",
        )
        raise exceptions.ValidationError(
            "The URN is not valid",
            code="is_urn_valid")
    pattern = get_pattern(urn)

    """
    The validation of URN format and whether URN belongs to a court should really
    be separate. However, supplying separate messages for these 2 validation errors
    could be seen as opening a backdoor for users to try and 'guess' valid URNs.

    This should be reviewed when DX data comes into play.
    """
    if not re.match(pattern, urn) or not Court.objects.has_court(urn):
        AuditEvent().populate(
            event_type="urn_validator",
            event_subtype="case_invalid_invalid_urn",
            event_trace="'is_urn_valid' found either no matching urn pattern or no matching court with URN {0}.format(urn)",
        )
        raise exceptions.ValidationError(
            "The URN is not valid",
            code="is_urn_valid")

    court = Court.objects.get_by_urn(urn)
    if court.validate_urn:
        if not Case.objects.filter(urn__iexact=urn, sent=False).exists():
            AuditEvent().populate(
                event_type="urn_validator",
                event_subtype="case_invalid_invalid_urn",
                event_trace="'is_urn_valid' found no unsent case matching a strictly validating court with URN {0}.format(urn)",
            )
            raise exceptions.ValidationError(
                "The URN is not valid",
                code="is_urn_valid")

    return True


def is_valid_urn_format(urn):
    urn = standardise_urn(urn)
    pattern = get_pattern(urn)

    if not re.match(pattern, urn):
        AuditEvent().populate(
            event_type="urn_validator",
            event_subtype="case_invalid_invalid_urn",
            event_trace="'is_valid_urn_format' found no matching urn pattern with URN {0}.format(urn)",
        )
        raise exceptions.ValidationError(
            "The URN is not valid",
            code="is_urn_valid")

    return True
