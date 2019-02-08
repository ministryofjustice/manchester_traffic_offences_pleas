import datetime as dt
from dateutil import parser
import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.text import wrap
from django.utils import translation
from django.utils.translation import ugettext as _

from .models import Case, CourtEmailCount, Court
from .encrypt import encrypt_and_store_user_data
from .tasks import email_send_court, email_send_prosecutor, email_send_user
from .standardisers import format_for_region, standardise_name


logger = logging.getLogger(__name__)


def get_plea_type(context_data):
    """
    Determine if pleas for a submission are
        all guilty  - returns "guilty"
        all not guilty - returns "not_guilty"
        or mixed - returns "mixed"
    """

    guilty_count = len([plea for plea in context_data["plea"]["data"]
                        if plea["guilty"] == "guilty_court" or plea["guilty"] == "guilty_no_court"])

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

    case = Case.objects.filter(
        urn__iexact=context_data["case"]["urn"].upper(), sent=False,
        imported=True).first()

    if not case:
        case = Case.objects.create(urn=context_data["case"]["urn"].upper(),
                                   sent=False,
                                   imported=False)

    court_obj = Court.objects.get_court(context_data["case"]["urn"], ou_code=case.ou_code)

    email_address = context_data.get("your_details", {}).get("email", False)
    email_address = email_address or context_data.get("company_details", {}).get("email", False)

    context_data["email"] = email_address

    # add DOH / name to the email subject for compliance with the current format
    if not context_data["notice_type"]["sjp"]:
        if isinstance(context_data["case"]["date_of_hearing"], str):
            date_of_hearing = parser.parse(context_data["case"]["date_of_hearing"])
        else:
            date_of_hearing = context_data["case"]["date_of_hearing"]

        context_data["email_date_of_hearing"] = date_of_hearing.strftime("%Y-%m-%d")

    if context_data["case"]["plea_made_by"] == "Defendant":
        first_name = context_data["your_details"]["first_name"]
        middle_name = context_data["your_details"]["middle_name"]
        last_name = context_data["your_details"]["last_name"]
    else:
        first_name = context_data["company_details"]["first_name"]
        middle_name = ""
        last_name = context_data["company_details"]["last_name"]

    if "date_of_birth" in context_data["case"]:
        context_data["your_details"]["date_of_birth"] = context_data["case"]["date_of_birth"]

    context_data["email_name"] = " ".join([last_name.upper(), first_name, middle_name]).strip()

    # Add Welsh flag if journey was completed in Welsh
    if translation.get_language() == "cy":
        context_data["welsh_language"] = True

    if context_data["notice_type"]["sjp"]:
        case.initiation_type = "J"

    case.language = translation.get_language().split("-")[0]
    case.name = standardise_name(first_name, last_name)
    case.completed_on = dt.datetime.now()

    if context_data["case"]["plea_made_by"] == "Company representative":
        if case.extra_data and "OrganisationName" in case.extra_data:
            case.extra_data["OrganisationName"] = context_data.get("company_details", {}).get("company_name")
        else:
            case.extra_data = {"OrganisationName": context_data.get("company_details", {}).get("company_name")}

    if email_address:
        case.email = email_address
        case.send_user_email = True

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

    if email_address:
        data = {
            "urn": format_for_region(context_data["case"]["urn"]),
            "plea_made_by": context_data["case"]["plea_made_by"],
            "number_of_charges": context_data["case"]["number_of_charges"],
            "contact_deadline": context_data["case"]["contact_deadline"],
            "plea_type": get_plea_type(context_data),
            "court_name": court_obj.court_name,
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
