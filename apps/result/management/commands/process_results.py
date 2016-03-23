# coding=utf-8
import datetime as dt
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.management.base import BaseCommand
from django.utils import translation
from django.template.loader import get_template
import re


from apps.result.models import Result
from apps.plea.models import Case, CaseOffenceFilter, Court
from apps.plea.standardisers import standardise_urn, StandardiserNoOutputException


class Command(BaseCommand):
    help = "Send out result emails"

    def mark_done(self, result, sent=False):
        result.processed = True
        if sent:
            result.sent = True
            result.sent_on = datetime.now()
        result.save()

    def handle(self, *args, **options):
        # May need to change to CY if we get a proper result language
        translation.activate("en")
        text_template = get_template("emails/user_resulting.txt")
        html_template = get_template("emails/user_resulting.html")

        processed_count = 0
        unprocessed_count = 0

        # Iterate through any results that don't have an adjournment code
        for result in Result.objects.filter(processed=False).exclude(result_offences__offence_data__result_code__in=["A", "ADJNN", "ADJN"]):
            # Only use results that we can match back to a sent case with an email address
            case = Case.objects.filter(case_number=result.case_number, email__isnull=False, sent=True)

            # ------ temporary code - only process results wtih a hearing date of today ------
            if dt.date.today() != result.date_of_hearing:
                continue
            # ------ end temp test code ------

            # ------ temporary test code - get a fake court
            c, created = Case.objects.get_or_create(
                case_number="resulting",
                defaults={
                    "name": "Test case",
                    "email": "hugh.ivory@agilesphere.eu",
                    "extra_data": {},
            })

            case = [c]
            # -------end of temporary code

            if len(case):
                # Shouldn't be more than one but just in case there is grab the first
                case = case[0]

                # Get out early if this result has offence codes we shouldn't be dealing with
                offence_codes = [offence.offence_code[:4] for offence in result.result_offences.all()]
                match = False

                # --- commented out whilst testing
                # for offence_code in offence_codes:
                #     if CaseOffenceFilter.objects.filter(filter_match__startswith=offence_code).exists():
                #         match = True
                #     else:
                #         match = False
                #         break
                #
                # if not match:
                #     unprocessed_count += 1
                #     self.mark_done(result)
                # --- end of commented out block

                total = Decimal()

                # Only process cases that have final codes (maybe this should be done in the initial result filtering?)
                if result.result_offences.filter(offence_data__result_code__startswith="F").exists():
                    data = {"urn": result.urn,
                            "fines": [],
                            "endorsements": []}

                    if case.name:
                        data["name"] = case.name
                    elif case.extra_data and "Forename1" in case.extra_data:
                        data["name"] = "{} {}".format(case.extra_data["Forename1"], case.extra_data["Surname"])
                    else:
                        data["name"] = ""

                    data["pay_by"] = result.pay_by_date
                    data["payment_details"] = {"division": result.division,
                                               "account_number": result.account_number}

                    # If we move to using OU codes in Case data this should be replaced by a lookup using the
                    # Case OU code
                    try:
                        data["court"] = Court.objects.get_by_urn(standardise_urn(result.urn))
                    except StandardiserNoOutputException:
                        print "URN failed to standardise: {}".format(result.urn)

                    # Loop through the offences and results and pick out what we need to display
                    fines = []
                    endorsements = []
                    for offence in result.result_offences.all():
                        for r in offence.offence_data.all():
                            if r.result_code.startswith("F"):
                                values = re.findall(r'\xa3([0-9]+\.*[0-9]{0,2})', r.result_wording)
                                value = sum(Decimal(v) for v in values)
                                total += value
                                fines.append({"label": r.result_wording})
                            elif r.result_code in ["LEP", ]:
                                endorsements.append(r.result_wording)
                            else:
                                print offence.offence_code, r.result_code, r.result_wording.encode("utf-8")

                    # Collect everything, render and send the email.
                    data["fines"] = fines
                    data["endorsements"] = endorsements
                    data["total"] = total

                    t_output = text_template.render(data)
                    h_output = html_template.render(data)

                    # Send email and mark as sent
                    connection = get_connection(host=settings.EMAIL_HOST,
                                                port=settings.EMAIL_PORT,
                                                username=settings.EMAIL_HOST_USER,
                                                password=settings.EMAIL_HOST_PASSWORD,
                                                use_tls=settings.EMAIL_USE_TLS)

                    recipients = [case.email]

                    recipients.append("lyndon.garvey@digital.justice.gov.uk")
                    recipients.append("s.walker-russell@hmcts.gsi.gov.uk ")
                    recipients.append("james.hehir@hmcts.gsi.gov.uk")

                    email = EmailMultiAlternatives("Make a plea result", t_output, settings.PLEA_CONFIRMATION_EMAIL_FROM,
                                                   recipients, connection=connection)

                    email.attach_alternative(h_output, "text/html")
                    # email.send(fail_silently=False)
                    print "Email sent to {}".format(case.email)

                    self.mark_done(result, sent=True)
                    processed_count += 1
            else:
                unprocessed_count += 1

        print "Processed: {}, skipped: {}".format(processed_count, unprocessed_count)
