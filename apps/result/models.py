from decimal import Decimal
import re

from django.db import models

from apps.plea.models import Case, CaseOffenceFilter


DO_NOT_RESULT_CODES = {
    "DDDT": "Discretionary with disqualification until ordinary test passed",
    "DDPR": "Points but reduced disqualification for mitigating circumstance",
    "DDOTE": "Obligatory disqualification until extended test passed",
    "DDOR": "Obligatory but reduced disqualification for special reasons",
    "DDP": "Points disqualification",
    "DDO": "Obligatory disqualification",
    "DDD": "Discretionary with ordinary disqualification",
    "DDPTE": "Points with disqualification until extended test passed",
    "DDRN": "Disqualification for non-endorsable offence",
    "DDRCOT": "Obligatory Disqualification until extended test passed - reduction for course",
    "DDRI": "Interim Disqualification",
    "DDDTO": "Discretionary disqualification until test passed only",
    "DDRCD": "Driving Disq - Reduction for course (discretionary)",
    "DDRCO": "Driving Disq - Reduction for course (obligatory)"
}


ADJOURNED_CODES = {
    "AREMHA": "Adjournment Adult Remittal Home Court Area",
    "AREMOA": "Adjournment Adult Remittal Other Court Area",
    "A": "Adjournment",
    "AINT": "Adjourn Interim Hearing",
    "AO": "Adjournment - Other Court Area",
    "ADJP": "Adjournment (Document requires personal service)",
    "AREMHY": "Adjournment Youth Remittal Home Court Area",
    "ACON": "Account Consolidated",
    "ADJNN": "Adjournment (No Notice)",
    "ASD": "Adjourned Sine Die"
}

WITHDRAWN_CODES = {
    "WDRN": "Withdrawn"
}


class Result(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    case = models.ForeignKey("plea.Case", related_name="results", null=True, blank=True)
    urn = models.CharField(max_length=30, db_index=True)

    case_number = models.CharField(max_length=12, null=True, blank=True,
                                   help_text="as supplied by DX")
    ou_code = models.CharField(max_length=10, null=True, blank=True)
    date_of_hearing = models.DateField()
    account_number = models.CharField(max_length=100, null=True, blank=True)
    division = models.CharField(max_length=100, null=True, blank=True)
    instalment_amount = models.CharField(max_length=100, null=True, blank=True)
    lump_sum_amount = models.CharField(max_length=100, null=True, blank=True)
    pay_by_date = models.DateField(null=True, blank=True)
    payment_type = models.CharField(max_length=10, null=True, blank=True)

    processed = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    sent_on = models.DateTimeField(null=True, blank=True)

    def has_valid_offences(self):
        """
        Are all the offences in this case whistlisted?
        """

        offence_codes = [offence.offence_code[:4] for offence in self.result_offences.all()]

        for offence_code in offence_codes:
            if CaseOffenceFilter.objects.filter(filter_match__startswith=offence_code).exists():
                return True

        return False

    def can_result(self):
        """
        Can a case be resulted?

        All offence results need to be fit the criteria below:

        1. All offence codes in scope / whitelisted? Yes, then we can result
        1. Disqualification? No result
        2. Does it have final codes? Yes, then we can result
        3. An offence has been adjourned? Yes, then we can't result
        4. An offence has been adjourned but subsequently withdrawn? If yes, then we can result
        """

        has_fine_codes = False

        case = self.get_associated_case()

        if not self.division or not self.account_number:
            return False, "Missing division code or account number"

        for result in self.result_offences.all():
            adjourned = False
            withdrawn = False

            offence_has_fine_codes = False

            for offence_data in result.offence_data.all():

                if offence_data.result_code in DO_NOT_RESULT_CODES:
                    return False, "out of scope result code: {}".format(offence_data.result_code)

                elif offence_data.result_code in ADJOURNED_CODES:
                    adjourned = True

                elif offence_data.result_code in WITHDRAWN_CODES:
                    withdrawn = True

            if adjourned and not withdrawn:
                return False, "adjournment"

        return True, ""

    def get_associated_case(self):
        """
        Return an associated and resultable case
        """

        cases = Case.objects.filter(case_number=self.case_number, email__isnull=False, sent=True)

        return cases[0] if cases else None

    def get_offence_totals(self):
        """
        Extract relevant offence information
        """

        total = Decimal()
        fines = []
        endorsements = []

        for offence in self.result_offences.all():
            for r in offence.offence_data.all():
                if r.result_code.startswith("F"):
                    values = re.findall(r'\xa3([0-9]+\.*[0-9]{0,2})', r.result_wording)
                    value = sum(Decimal(v) for v in values)
                    total += value
                    fines.append(r.result_wording_by_language)

                elif r.result_code in ["LEP", "LEA"]:
                    endorsements.append(r.result_wording_by_language)

        return fines, endorsements, total


class ResultOffence(models.Model):
    result = models.ForeignKey(Result, related_name="result_offences")

    offence_code = models.CharField(max_length=10, null=True, blank=True)
    offence_seq_number = models.CharField(max_length=10, null=True, blank=True)


class ResultOffenceData(models.Model):
    result_offence = models.ForeignKey(ResultOffence, related_name="offence_data")

    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_short_title = models.CharField(max_length=120)
    result_short_title_welsh = models.CharField(max_length=120, null=True, blank=True)
    result_wording = models.TextField(max_length=4000)
    result_wording_welsh = models.TextField(max_length=4000, null=True, blank=True)
    result_seq_number = models.CharField(max_length=10, null=True, blank=True)

    @property
    def language(self):
        return getattr(self.result_offence.result.case, 'language', 'en')

    @property
    def result_short_title_by_language(self):
        if self.language == "cy" and self.result_short_title_welsh and self.result_short_title_welsh.strip():
            return self.result_short_title_welsh
        else:
            return self.result_short_title

    @property
    def result_wording_by_language(self):
        if self.language == "cy" and self.result_wording_welsh and self.result_wording_welsh.strip():
            return self.result_wording_welsh
        else:
            return self.result_wording

