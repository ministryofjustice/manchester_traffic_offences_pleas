from copy import deepcopy
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
from .models import Case, CourtEmailCount, Court
from .encrypt import encrypt_and_store_user_data


logger = logging.getLogger(__name__)


def send_user_confirmation_email(context_data):
    """
    Dispatch an email to the user to confirm that their plea submission
    was successful.
    """

    from .stages import get_plea_type

    if context_data['case']['company_plea']:
        email = context_data['company_details']['email']
        name = context_data['company_details']['name']
    else:
        email = context_data['your_details']['email']
        name = context_data['your_details']['name']

    data = {
        'email': email,
        'urn': context_data['case']['urn'],
        'number_of_charges': context_data['case']['number_of_charges'],
        'plea_type': get_plea_type(context_data),
        'name': name,
        'court_address': context_data["court"].court_address,
        'court_email': context_data["court"].court_email
    }

    html_body = render_to_string("plea/plea_email_confirmation.html", data)
    txt_body = render_to_string("plea/plea_email_confirmation.txt", data)

    subject = settings.PLEA_CONFIRMATION_EMAIL_SUBJECT.format(**data)

    connection = get_connection(host=settings.USER_SMTP_EMAIL_HOST,
                                port=settings.USER_SMTP_EMAIL_PORT,
                                username=settings.USER_SMTP_EMAIL_HOST_USERNAME,
                                password=settings.USER_SMTP_EMAIL_HOST_PASSWORD,
                                use_tls=True)

    email = EmailMultiAlternatives(
        subject, txt_body, settings.PLEA_CONFIRMATION_EMAIL_FROM,
        [data['email']], connection=connection)

    email.attach_alternative(html_body, "text/html")

    try:
        email.send(fail_silently=False)
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        logger.error("Error sending email: {0}".format(e))

    return True


def send_plea_email(context_data, plea_email_to=None, send_user_email=False):
    """
    Sends a plea email. All addresses, content etc. are defined in
    settings.

    context_data: dict populated by form fields
    """

    try:
        court_obj = Court.objects.get_by_urn(context_data["case"]["urn"])
    except Court.DoesNotExist:
        logger.error("A URN does not have a matching Court entry. Cannot proceed.")
        raise

    email_context = deepcopy(context_data)
    email_context["court"] = court_obj

    if plea_email_to is None:
        plea_email_to = [court_obj.submission_email]

    plea_email = TemplateAttachmentEmail(settings.PLEA_EMAIL_FROM,
                                         settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                         settings.PLEA_EMAIL_TEMPLATE,
                                         email_context,
                                         "text/html")

    plp_email = TemplateAttachmentEmail(settings.PLP_EMAIL_FROM,
                                        settings.PLEA_EMAIL_ATTACHMENT_NAME,
                                        settings.PLP_EMAIL_TEMPLATE,
                                        email_context,
                                        "text/html")

    # add DOH / name to the email subject for compliance with the current format
    if isinstance(context_data["case"]["date_of_hearing"], basestring):
        date_of_hearing = parser.parse(context_data["case"]["date_of_hearing"])
    else:
        date_of_hearing = context_data["case"]["date_of_hearing"]

    if context_data["case"]["company_plea"]:
        name = context_data["company_details"]["name"]
    else:
        name = context_data["your_details"]["name"]

    names = [name.rsplit(" ", 1)[-1].upper()]
    first_names = " ".join(name.rsplit(" ", 1)[:-1])
    if first_names:
        names.append(first_names)

    context_data["email_name"] = " ".join(names)
    context_data["email_date_of_hearing"] = date_of_hearing.strftime("%Y-%m-%d")

    case = Case()
    case.urn = context_data["case"]["urn"].upper()
    case.save()

    if "court" in context_data:
        del context_data["court"]

    if getattr(settings, 'STORE_USER_DATA', False):
        encrypt_and_store_user_data(case.urn, case.id, context_data)

    if not court_obj.test_mode:
        # don't add test court entries to the anon stat data
        email_count = CourtEmailCount()
        email_count.get_from_context(context_data)
        email_count.save()

        email_count_id = email_count.id

    else:
        # use a fake email count ID as we're using a test record
        email_count_id = "XX"

    email_body = "<<<makeaplea-ref: {}/{}>>>".format(case.id, email_count_id)

    try:
        plea_email.send(plea_email_to,
                        settings.PLEA_EMAIL_SUBJECT.format(**context_data),
                        email_body,
                        route="GSI")
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        case.status = "network_error"
        case.status_info = unicode(e)
        if not court_obj.test_mode:
            email_count.get_status_from_case(case)
            email_count.save()
        case.save()
        return False

    if not court_obj.test_mode:
        # again, only update anon stats if we're not using a test court
        case.status = "sent"
        case.save()
        email_count.get_status_from_case(case)
        email_count.save()

    if court_obj.plp_email:
        # only send the plp email if Court.plp_email is occupied
        try:
            plp_email.send([court_obj.plp_email],
                           settings.PLP_EMAIL_SUBJECT.format(**context_data),
                           settings.PLEA_EMAIL_BODY,
                           route="GSI")
        except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
            logger.error("Error sending email: {0}".format(e.message))

    send_user_confirmation_email(email_context)

    return True
