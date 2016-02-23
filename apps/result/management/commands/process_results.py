# coding=utf-8
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import translation
from django.template.loader import get_template
import re


from apps.result.models import Result
from apps.plea.models import Case, Court
from apps.plea.standardisers import standardise_urn, StandardiserNoOutputException




"""
Needs:
URN
name
court
fines
- label
- amount
total
endorsements
"""


class Command(BaseCommand):
    help = "Send out result emails"

    def handle(self, *args, **options):
        # May need to change to CY if we get a proper result language
        translation.activate("en")
        text_template = get_template("emails/user_resulting.txt")
        html_template = get_template("emails/user_resulting.html")
        # Need a better filter than sent ... most of these will never get sent
        # maybe add a processed flag to the result obj
        count = 0
        for result in Result.objects.filter(sent=False, result_offences__offence_data__result_code="GPTAC"):
            case = Case.objects.filter(case_number=result.case_number)
            if len(case):
                case = case[0]
                total = Decimal()
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

                    try:
                        data["court"] = Court.objects.get_by_urn(standardise_urn(result.urn))
                    except StandardiserNoOutputException:
                        print "URN failed to standardise: {}".format(result.urn)

                    fines = []
                    endorsements = []
                    for offence in result.result_offences.all():
                        for r in offence.offence_data.all():
                            if r.result_code.startswith("F"):
                                values = re.findall(r'\xa3([0-9]+\.*[0-9]{0,2})', r.result_wording)
                                value = sum(Decimal(v) for v in values)
                                total += value
                                fines.append({"label": r.result_wording})
                            elif r.result_code in ["DDP", "LEP"]:
                                endorsements.append(r.result_wording)
                            else:
                                print offence.offence_code, r.result_code, r.result_wording.encode("utf-8")

                    data["fines"] = fines
                    data["endorsements"] = endorsements
                    data["total"] = total

                    t_output = text_template.render(data)
                    h_output = html_template.render(data)

                    # Send email and mark as sent
                    print t_output.encode("utf-8")
                    count += 1
                    if count > 10:
                        break
