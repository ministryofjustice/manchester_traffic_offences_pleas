from __future__ import absolute_import

import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.utils import translation

from apps.plea.gov_notify import GovNotify

from celery import shared_task

from apps.plea.models import Case, CourtEmailCount, Court
from apps.plea.standardisers import format_for_region

logger = logging.getLogger(__name__)


def get_email_subject(email_data):
    if email_data["notice_type"]["sjp"] is True:
        subject = "ONLINE PLEA: {case[formatted_urn]} <SJP> {email_name}"
    else:
        subject = "ONLINE PLEA: {case[formatted_urn]} DOH: {email_date_of_hearing} {email_name}"

    email_data["case"]["formatted_urn"] = format_for_region(email_data["case"]["urn"])
    return subject.format(**email_data)


def get_email_body(case, count_id):
    return "<<<makeaplea-ref: {}/{}>>>".format(case.id, count_id)


def get_court(urn, ou_code):
    try:
        court_obj = Court.objects.get_court(urn, ou_code=ou_code)
    except Court.DoesNotExist:
        logger.warning("URN does not have a matching Court entry: {}".format(urn))
        raise
    return court_obj


def is_18_or_under(date_of_birth):
    if not isinstance(date_of_birth, date):
        return False

    target_date = (datetime.today() - relativedelta(years=18)).date()

    return date_of_birth >= target_date


def get_smtp_gateway(email_address):
    if email_address.endswith('gsi.gov.uk'):
        return "GSI"
    return "PUB"


@shared_task(bind=True, max_retries=10, default_retry_delay=900)
def email_send_court(self, case_id, count_id, email_data):
    email_data["urn"] = format_for_region(email_data["case"]["urn"])

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)

    court_obj = get_court(email_data["case"]["urn"], case.ou_code)

    plea_email_to = court_obj.submission_email

    email_count = None
    if not court_obj.test_mode:
        email_count = CourtEmailCount.objects.get(pk=count_id)

    case.add_action("Court email started", "")

    email_subject = get_email_subject(email_data)
    email_body = get_email_body(case, count_id)

    personalisation = {
        "subject": email_subject,
        "email_body": email_body
    }
    plea_email = GovNotify(
        email_address=plea_email_to,
        personalisation=personalisation,
        template_id='d91127f7-814c-4b03-a1fd-10fd5630a49b'
    )

    plea_email.upload_file_link(email_data, 'emails/attachments/plea_email.html')

    try:
        with translation.override("en"):
            plea_email.send_email()
    except Exception as exc:
        logger.warning("Error sending email to court: {0}".format(exc))
        case.add_action("Court email network error", u"{}: {}".format(type(exc), exc))
        if email_count is not None:
            email_count.get_status_from_case(case)
            email_count.save()
        case.sent = False
        case.save()

    case.add_action("Court email sent", "Sent mail to {0} via {1}".format(
        plea_email_to, 'make.a.plea@notifications.service.gov.uk'))

    if not court_obj.test_mode:
        case.sent = True
        case.save()

        email_count.get_status_from_case(case)
        email_count.save()

    return True


@shared_task(bind=True, max_retries=10, default_retry_delay=1800)
def email_send_prosecutor(self, case_id, email_data):

    email_data["urn"] = format_for_region(email_data["case"]["urn"])

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(pk=case_id)

    court_obj = get_court(email_data["case"]["urn"], case.ou_code)

    case.add_action("Prosecutor email started", "")

    email_subject = "POLICE " + get_email_subject(email_data)
    email_body = ""

    email_data["your_details"]["18_or_under"] = is_18_or_under(
        email_data["your_details"].get("date_of_birth"))

    if court_obj.plp_email:

        personalisation = {
            "subject": email_subject,
            "email_body": email_body
        }
        plp_email = GovNotify(
            email_address=court_obj.plp_email,
            personalisation=personalisation,
            template_id='d91127f7-814c-4b03-a1fd-10fd5630a49b'
        )

        plp_email.upload_file_link(email_data, 'emails/attachments/plp_email.html')

        try:
            with translation.override("en"):
                plp_email.send_email()
        except Exception as exc:
            logger.warning("Error sending email to prosecutor: {0}".format(exc))
            case.add_action("Prosecutor email network error", u"{}: {}".format(type(exc), exc))
            raise self.retry(args=[case_id, email_data], exc=exc)

        case.add_action("Prosecutor email sent", "Sent mail to {0} via {1}".format(
            court_obj.plp_email, 'make.a.plea@notifications.service.gov.uk'))

    else:
        case.add_action("Prosecutor email not sent", "No plp email in court data")

    return True


@shared_task(bind=True, max_retries=10, default_retry_delay=1800)
def email_send_user(self, case_id, email_address, subject, txt_body):
    """
    Dispatch an email to the user to confirm that their plea submission
    was successful.
    """

    # No error trapping, let these fail hard if the objects can't be found
    case = Case.objects.get(id=case_id)
    case.add_action("User email started", "")

    personalisation = {
        "subject": subject,
        "email_body": txt_body,
        "link_to_file": ''
    }
    user_email = GovNotify(
        email_address=email_address,
        personalisation=personalisation,
        template_id='d91127f7-814c-4b03-a1fd-10fd5630a49b'
    )

    try:
        user_email.send_email()
    except Exception as exc:
        logger.warning("Error sending user confirmation email: {0}".format(exc))
        case.add_action("User email network error", u"{}: {}".format(type(exc), exc))
        raise self.retry(args=[case_id, email_address, subject, txt_body], exc=exc)

    case.add_action("User email sent", "")

    return True
