from dateutil import parser
import logging
import json
import smtplib
import socket

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation

from apps.govuk_utils.email import TemplateAttachmentEmail

from .models import Case, CourtEmailCount, Court
from .encrypt import encrypt_and_store_user_data
from tasks import email_send_court, email_send_prosecutor, email_send_user


logger = logging.getLogger(__name__)


def send_plea_email(context_data):
    """
    Sends a plea email. All addresses, content etc. are defined in
    settings.

    context_data: dict populated by form fields
    """
    try:
        court_obj = Court.objects.get_by_urn(context_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.error("URN does not have a matching Court entry: {}".format(
            context_data["case"]["urn"]))
        raise

    # add DOH / name to the email subject for compliance with the current format
    if isinstance(context_data["case"]["date_of_hearing"], basestring):
        date_of_hearing = parser.parse(context_data["case"]["date_of_hearing"])
    else:
        date_of_hearing = context_data["case"]["date_of_hearing"]

    if context_data["case"]["plea_made_by"] == "Defendant":
        first_name = context_data["your_details"]["first_name"]
        last_name = context_data["your_details"]["last_name"]
    else:
        first_name = context_data["company_details"]["first_name"]
        last_name = context_data["company_details"]["last_name"]

    context_data["email_name"] = " ".join([last_name.upper(), first_name])
    context_data["email_date_of_hearing"] = date_of_hearing.strftime("%Y-%m-%d")

    # Add Welsh flag if journey was completed in Welsh
    if translation.get_language() == "cy":
        context_data["welsh_language"] = True

    # Get or create case
    try:
        case = Case.objects.get(urn__iexact=context_data["case"]["urn"].upper(), sent=False)
    except Case.DoesNotExist:
        case = Case(urn=context_data["case"]["urn"].upper(), sent=False)
        case.save()

    if "court" in context_data:
        del context_data["court"]

    if getattr(settings, 'STORE_USER_DATA', False):
        encrypt_and_store_user_data(case.urn, case.id, context_data)

    if not court_obj.test_mode:
        # don't add test court entries to the anon stat data
        email_count = CourtEmailCount()
        email_count.get_from_context(context_data, court=court_obj)
        email_count.save()

        email_count_id = email_count.id

    else:
        # use a fake email count ID as we're using a test record
        email_count_id = "XX"

    email_body = "<<<makeaplea-ref: {}/{}>>>".format(case.id, email_count_id)

    email_send_court.delay(case.id, email_count_id, context_data)

    case.add_action("Sent", "Email tasks created")
    case.sent = True
    case.save()

    if not court_obj.test_mode:
        email_count.sent = True
        email_count.save()

    if court_obj.plp_email:
        email_send_prosecutor.delay(case.id, context_data)

    email_send_user.delay(case.id, context_data)

    return True
