from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from apps.forms.stages import FormStage, IndexedStage

from .email import send_plea_email, get_plea_type
from .forms import (NoticeTypeForm,
                    CaseForm,
                    SJPCaseForm,
                    YourDetailsForm,
                    CompanyDetailsForm,
                    PleaForm,
                    SJPPleaForm,
                    YourStatusForm,
                    YourFinancesEmployedForm,
                    YourFinancesSelfEmployedForm,
                    YourFinancesBenefitsForm,
                    YourFinancesOtherForm,
                    HardshipForm,
                    HouseholdExpensesForm,
                    OtherExpensesForm,
                    CompanyFinancesForm,
                    ConfirmationForm)

from .fields import ERROR_MESSAGES
from .models import Court, Case, Offence
from .standardisers import get_standardiser


def get_case(urn):
    try:
        return Case.objects.get(urn__iexact=urn, sent=False)
    except (Case.DoesNotExist, MultipleObjectsReturned):
        return None


def get_offences(case_data):
        urn = case_data.get("urn")
        # TODO: change this to grabbing by case OU or a FK at some point

        offences = []
        if urn:
            case = get_case(urn)
            court = Court.objects.get_by_urn(urn)

            # offence_seq_number is a char field so best to cast and order by
            # rather than just grabbing case.offences.all() and hoping it's
            # in the right order
            if court.display_case_data:
                offences = Offence.objects.filter(case=case).extra(
                    select={"seq_number": "cast(coalesce(nullif(offence_seq_number,''),'0') as float)"}
                ).order_by("seq_number", "id")

        return offences


class NoticeTypeStage(FormStage):
    name = "notice_type"
    template = "notice_type.html"
    form_class = NoticeTypeForm
    dependencies = []


class CaseStage(FormStage):
    name = "case"
    template = "case.html"
    form_class = CaseForm
    dependencies = ["notice_type"]

    def __init__(self, *args, **kwargs):
        super(CaseStage, self).__init__(*args, **kwargs)
        try:
            if self.all_data["notice_type"]["sjp"]:
                self.form_class = SJPCaseForm
        except KeyError:
            pass

    def render(self, request_context):
        if "urn" in self.form.errors and ERROR_MESSAGES["URN_ALREADY_USED"] in self.form.errors["urn"]:
            self.context["urn_already_used"] = True

            try:
                self.context["court"] = Court.objects.get_by_urn(self.form.data["urn"])
            except Court.DoesNotExist:
                pass

        return super(CaseStage, self).render(request_context)

    def save(self, form_data, next_step=None):
        clean_data = super(CaseStage, self).save(form_data, next_step)

        if "urn" in clean_data:
            standardise = get_standardiser(clean_data["urn"])
            clean_data["urn"] = standardise(clean_data["urn"])
            offences = get_offences(clean_data)
            if offences:
                clean_data["number_of_charges"] = len(offences)

        # Set the court contact deadline
        if "date_of_hearing" in clean_data:
            clean_data["contact_deadline"] = clean_data["date_of_hearing"]

        if "posting_date" in clean_data:
            clean_data["contact_deadline"] = clean_data["posting_date"] + relativedelta(days=+28)

        if "complete" in clean_data:
            if clean_data.get("plea_made_by", "Defendant") == "Defendant":
                self.set_next_step("your_details")
            else:
                self.set_next_step("company_details")

        return clean_data


class CompanyDetailsStage(FormStage):
    name = "company_details"
    template = "company_details.html"
    form_class = CompanyDetailsForm
    dependencies = ["notice_type", "case"]

    def save(self, form_data, next_step=None):
        clean_data = super(CompanyDetailsStage,
                           self).save(form_data, next_step)

        if "complete" in clean_data:
            self.set_next_step("plea", skip=["your_details", "your_finances", "household_expenses"])

        return clean_data


class YourDetailsStage(FormStage):
    name = "your_details"
    template = "your_details.html"
    form_class = YourDetailsForm
    dependencies = ["notice_type", "case"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourDetailsStage,
                           self).save(form_data, next_step)

        if "complete" in clean_data:
            self.set_next_step("plea", skip=["company_details",
                                             "company_finances"])

        return clean_data


class PleaStage(IndexedStage):
    name = "plea"
    template = "plea.html"
    form_class = PleaForm
    dependencies = ["notice_type", "case", "your_details", "company_details"]

    def __init__(self, *args, **kwargs):
        super(PleaStage, self).__init__(*args, **kwargs)
        try:
            if self.all_data["notice_type"]["sjp"] is True:
                self.form_class = SJPPleaForm
        except KeyError:
            pass

    def load_forms(self, data=None, initial=False):
        initial_data = None
        # TODO: change this to grabbing by case OU or a FK at some point
        offences = get_offences(self.all_data["case"])

        if initial:
            data = self.all_data.get(self.name, {}).get("data", [])
            try:
                initial_data = data[self.index-1]
            except IndexError:
                pass

            if self.form_class:
                self.form = self.form_class(initial=initial_data, label_suffix="")
        else:
            if self.form_class:
                self.form = self.form_class(data, label_suffix="")

        if offences:
            try:
                self.form.case_data = offences[self.index-1]
            except IndexError:
                pass

    def save(self, form_data, next_step=None):
        clean_data = super(PleaStage, self).save(form_data, next_step)
        plea_count = self.all_data["case"]["number_of_charges"]
        stage_data = self.all_data[self.name]
        stage_data["none_guilty"] = True
        offences = get_offences(self.all_data["case"])

        if "data" not in stage_data:
            stage_data["data"] = []

        if len(stage_data["data"]) < self.index:
            stage_data["data"].append({})

        stage_data["data"][self.index-1] = clean_data

        for plea in stage_data["data"]:
            if plea.get("guilty") == "guilty":
                stage_data["none_guilty"] = False
                break

        try:
            stage_data["data"][self.index-1]["title"] = offences[self.index-1].offence_short_title
        except IndexError:
            pass

        if "guilty" not in stage_data["data"][self.index-1]:
            return clean_data

        if self.split_form is None or self.split_form == "split_form_last_step":
            if self.index < plea_count:
                self.next_step = reverse("plea_form_step", kwargs={"stage": self.name, "index": self.index+1})
            else:
                if self.all_data["case"].get("plea_made_by", "Defendant") == "Company representative":
                    if stage_data["none_guilty"]:
                        self.set_next_step("review", skip=["company_finances",
                                                           "your_status", "your_finances"])
                    else:
                        self.set_next_step("company_finances", skip=["your_status", "your_finances"])
                else:
                    if stage_data["none_guilty"]:
                        self.set_next_step("review", skip=["your_status", "your_finances"])
                    elif "skipped" in self.all_data["your_status"]:
                        del self.all_data["your_status"]["skipped"]

        return stage_data

    def render(self, request_context):
        self.context["index"] = self.index
        return super(PleaStage, self).render(request_context)


class CompanyFinancesStage(FormStage):
    name = "company_finances"
    template = "company_finances.html"
    form_class = CompanyFinancesForm
    dependencies = ["notice_type", "case"]


class YourStatusStage(FormStage):
    name = "your_status"
    template = "your_status.html"
    form_class = YourStatusForm
    dependencies = ["notice_type", "case", "your_details", "plea"]

class YourFinancesStage(FormStage):
    name = "your_finances"
    form_class = YourFinancesEmployedForm
    template = "your_finances.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status"]

    def __init__(self, *args, **kwargs):
        super(YourFinancesStage, self).__init__(*args, **kwargs)

        finance_forms = {
            "Employed": YourFinancesEmployedForm,
            "Self-employed": YourFinancesSelfEmployedForm,
            "Receiving benefits": YourFinancesBenefitsForm,
            "Other": YourFinancesOtherForm
        }

        try:
            self.form_class = finance_forms.get(self.all_data["your_status"]["you_are"], YourFinancesEmployedForm)
        except KeyError:
            pass


    def load(self, request_context=None):
        return super(YourFinancesStage, self).load(request_context)

    def save(self, form_data, next_step=None):

        clean_data = super(YourFinancesStage, self).save(form_data, next_step)

        you_are = self.all_data["your_status"]["you_are"]

        if you_are:
            hardship_field = you_are.replace(" ", "_").replace("-", "_").lower() + "_hardship"

            hardship = clean_data.get(hardship_field, False)

            self.all_data["your_finances"]["hardship"] = hardship

            if not hardship:
                self.set_next_step("review", skip=["hardship", "household_expenses", "other_expenses"])

        return clean_data


class HardshipStage(FormStage):
    name = "hardship"
    template = "hardship.html"
    form_class = HardshipForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "plea",
                    "your_status",
                    "your_finances"]


class HouseholdExpensesStage(FormStage):
    name = "household_expenses"
    template = "household_expenses.html"
    form_class = HouseholdExpensesForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "plea",
                    "your_status",
                    "your_finances",
                    "hardship"]

    def save(self, form_data, next_step=None):

        household_expense_fields = ["household_accommodation",
                                    "household_utility_bills",
                                    "household_insurance",
                                    "household_council_tax"]

        clean_data = super(HouseholdExpensesStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            total_household = sum(float(clean_data[field] or 0) for field in household_expense_fields)
            self.all_data["your_expenses"] = {"total_household_expenses": total_household}

        return clean_data


class OtherExpensesStage(FormStage):
    name = "other_expenses"
    template = "other_expenses.html"
    form_class = OtherExpensesForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "plea",
                    "your_status",
                    "your_finances",
                    "hardship",
                    "household_expenses"]

    def save(self, form_data, next_step=None):

        other_expense_fields = ["other_tv_subscription",
                                "other_travel_expenses",
                                "other_telephone",
                                "other_loan_repayments",
                                "other_court_payments",
                                "other_child_maintenance"]

        clean_data = super(OtherExpensesStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            self.set_next_step("review", skip=["company_finances"])

            total_household = self.all_data["your_expenses"]["total_household_expenses"]

            total_other = sum(float(clean_data[field] or 0) for field in other_expense_fields)
            total_expenses = total_household + total_other

            self.all_data["your_expenses"].update({"total_other_expenses": total_other,
                                                   "total_expenses": total_expenses })

        return clean_data


class ReviewStage(FormStage):
    name = "review"
    template = "review.html"
    form_class = ConfirmationForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "company_details",
                    "plea",
                    "your_status",
                    "your_finances",
                    "hardship",
                    "household_expenses",
                    "other_expenses",
                    "company_finances"]

    def save(self, form_data, next_step=None):
        clean_data = super(ReviewStage, self).save(form_data, next_step)

        try:
            self.all_data["case"]["urn"]
        except KeyError:
            # session has timed out
            self.add_message(messages.ERROR, "Your session has timed out",
                             extra_tags="session_timeout")

            self.set_next_step("case")
            return clean_data

        if clean_data.get("complete", False):
            email_data = {k: v for k, v in self.all_data.items()}
            email_data.update({"review": clean_data})
            email_result = send_plea_email(email_data)
            if email_result:
                self.set_next_step("complete")
            else:
                self.add_message(messages.ERROR, '<h2 class="heading-medium">{}</h2><p>{}</p>'.format(
                    _("Submission Error"),
                    _("There seems to have been a problem submitting your plea. Please try again.")))
                self.set_next_step("review")

        return clean_data


class CompleteStage(FormStage):
    name = "complete"
    template = "complete.html"
    form_class = None
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "company_details",
                    "plea",
                    "your_status",
                    "your_finances",
                    "hardship",
                    "household_expenses",
                    "other_expenses",
                    "company_finances",
                    "review"]

    def __init__(self, *args, **kwargs):
        super(CompleteStage, self).__init__(*args, **kwargs)
        try:
            if self.all_data["notice_type"]["sjp"]:
                self.template = "complete_sjp.html"
        except KeyError:
            pass

    def render(self, request_context):

        self.context["plea_type"] = get_plea_type(self.all_data)

        try:
            self.context["court"] = Court.objects.get_by_urn(self.all_data["case"]["urn"])
        except Court.DoesNotExist:
            pass

        # Build an array of events to send to analytics now the journey is complete
        def is_entered(field):
            if len(self.all_data.get("your_details", {}).get(field, "")) > 0:
                return "Yes"
            else:
                return "No"

        self.context["analytics_events"] = [{"action": "Plea made by",
                                             "label": self.all_data.get("case").get("plea_made_by")}]

        if self.all_data["case"]["plea_made_by"] == "Defendant":
            self.context["analytics_events"].extend([{"action": "NI number",
                                                      "label": is_entered("ni_number")},
                                                     {"action": "Driving licence number",
                                                      "label": is_entered("driving_licence_number")}])

        return super(CompleteStage, self).render(request_context)
