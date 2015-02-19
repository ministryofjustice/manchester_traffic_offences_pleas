from dateutil import parser
import logging
import json
import smtplib
import socket

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.conf import settings
from django.template.loader import render_to_string

from apps.govuk_utils.email import TemplateAttachmentEmail
from .models import Case, CourtEmailCount
from .encrypt import encrypt_and_store_user_data
from tasks import email_send_court, email_send_prosecutor, email_send_user


logger = logging.getLogger(__name__)


def send_plea_email(context_data, plea_email_to=None, send_user_email=False):
    """
    Sends a plea email. All addresses, content etc. are defined in
    settings.

    context_data: dict populated by form fields
    """

    # add DOH / name to the email subject for compliance with the current format
    if isinstance(context_data["case"]["date_of_hearing"], basestring):
        date_of_hearing = parser.parse(context_data["case"]["date_of_hearing"])
    else:
        date_of_hearing = context_data["case"]["date_of_hearing"]
    names = [context_data["your_details"]["name"].rsplit(" ", 1)[-1].upper()]
    first_names = " ".join(context_data["your_details"]["name"].rsplit(" ", 1)[:-1])
    if first_names:
        names.append(first_names)

    context_data["email_name"] = " ".join(names)
    context_data["email_date_of_hearing"] = date_of_hearing.strftime("%Y-%m-%d")

    case = Case()
    case.urn = context_data["case"]["urn"].upper()
    case.save()

    if getattr(settings, 'STORE_USER_DATA', False):
        encrypt_and_store_user_data(case.urn, case.id, context_data)

    email_count = CourtEmailCount()
    email_count.get_from_context(context_data)
    email_count.save()

    email_send_court.delay(case.id, email_count.id, context_data)

    return True