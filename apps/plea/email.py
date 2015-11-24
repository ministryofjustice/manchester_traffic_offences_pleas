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
from standardisers import format_for_region


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
    cases = Case.objects.filter(urn__iexact=context_data["case"]["urn"].upper(), sent=False)
    if len(cases) == 0:
        case = Case(urn=context_data["case"]["urn"].upper(), sent=False)
    else:
        case = cases[0]

    if context_data["notice_type"]["sjp"]:
        case.initiation_type = "J"

    case.language = translation.get_language().split("-")[0]
    case.save()

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

    send_user_email = context_data.get("review", {}).get("receive_email_updates", False)
    email_address = context_data.get("review", {}).get("email", False)

    if send_user_email and email_address:
        data = {
            "urn": format_for_region(context_data["case"]["urn"]),
            "plea_made_by": context_data["case"]["plea_made_by"],
            "number_of_charges": context_data["case"]["number_of_charges"],
            "contact_deadline": context_data["case"]["contact_deadline"],
            "plea_type": get_plea_type(context_data),
            "court_address": court_obj.court_address,
            "court_email": court_obj.court_email
        }

        email_template = "emails/user_plea_confirmation"

        try:
            if context_data["notice_type"]["sjp"]:
                email_template = "emails/user_plea_confirmation_sjp"
        except KeyError:
            pass

        html_body = render_to_string(email_template + ".html", data)
        txt_body = wrap(render_to_string(email_template + ".txt", data), 72)

        subject = _("Online plea submission confirmation")

        email_send_user.delay(case.id, email_address, subject, html_body, txt_body)

    else:
        case.add_action("No email entered, user email not sent", "")

    return True
