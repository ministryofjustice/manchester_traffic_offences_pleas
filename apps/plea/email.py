from dateutil import parser
import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.text import wrap
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from .models import Case, CourtEmailCount, Court
from .encrypt import encrypt_and_store_user_data
from tasks import email_send_court, email_send_prosecutor, email_send_user


logger = logging.getLogger(__name__)


def get_plea_type(context_data):
    """
    Determine if pleas for a submission are
        all guilty  - returns "guilty"
        all not guilty - returns "not_guilty"
        or mixed - returns "mixed"
    """

    guilty_count = len([plea for plea in context_data["plea"]["data"]
                        if plea["guilty"] == "guilty"])

    if guilty_count == 0:
        return "not_guilty"
    elif guilty_count == len(context_data["plea"]["data"]):
        return "guilty"
    else:
        return "mixed"


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
    if context_data["notice_type"]["sjp"] is False:
        if isinstance(context_data["case"]["date_of_hearing"], basestring):
            date_of_hearing = parser.parse(context_data["case"]["date_of_hearing"])
        else:
            date_of_hearing = context_data["case"]["date_of_hearing"]

        context_data["email_date_of_hearing"] = date_of_hearing.strftime("%Y-%m-%d")

    if context_data["case"]["plea_made_by"] == "Defendant":
        first_name = context_data["your_details"]["first_name"]
        last_name = context_data["your_details"]["last_name"]
    else:
        first_name = context_data["company_details"]["first_name"]
        last_name = context_data["company_details"]["last_name"]

    context_data["email_name"] = " ".join([last_name.upper(), first_name])

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

    if getattr(settings, "STORE_USER_DATA", False):
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

    email_send_court.delay(case.id, email_count_id, context_data)

    if court_obj.plp_email:
        email_send_prosecutor.delay(case.id, context_data)

    email_address = context_data.get("review", {}).get("email", False)

    if not email_address:
        case.add_action("No email entered, user email not sent", "")
        return True

    data = {
        "urn": context_data["case"]["urn"],
        "plea_made_by": context_data["case"]["plea_made_by"],
        "number_of_charges": context_data["case"]["number_of_charges"],
        "plea_type": get_plea_type(context_data),
        "court_address": court_obj.court_address,
        "court_email": court_obj.court_email
    }

    html_body = render_to_string("emails/user_plea_confirmation.html", data)
    txt_body = wrap(render_to_string("emails/user_plea_confirmation.txt", data), 72)

    subject = _("Online plea submission confirmation")

    email_send_user.delay(case.id, email_address, subject, html_body, txt_body)

    case.sent = True
    case.save()

    if not court_obj.test_mode:
        email_count.sent = True
        email_count.save()

    return True
