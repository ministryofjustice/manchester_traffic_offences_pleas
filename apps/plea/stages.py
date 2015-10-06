from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext as _

from apps.forms.stages import FormStage
from apps.forms.forms import RequiredFormSet

from .email import send_plea_email, get_plea_type
from .forms import (CaseForm,
                    YourDetailsForm,
                    CompanyDetailsForm,
                    PleaForm,
                    YourMoneyForm,
                    HardshipForm,
                    HouseholdExpensesForm,
                    OtherExpensesForm,
                    CompanyFinancesForm,
                    ConfirmationForm)

from .fields import ERROR_MESSAGES
from .models import Court, Case, Offence
from .standardisers import standardise_urn, slashify_urn


def get_case(urn):
    try:
        return Case.objects.get(urn__iexact=urn, sent=False)
    except (Case.DoesNotExist, MultipleObjectsReturned):
        return None


class CaseStage(FormStage):
    name = "case"
    template = "case.html"
    form_class = CaseForm
    dependencies = []

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
            clean_data["urn"] = slashify_urn(standardise_urn(clean_data["urn"]))

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
    dependencies = ["case"]

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
    dependencies = ["case"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourDetailsStage,
                           self).save(form_data, next_step)

        if "complete" in clean_data:
            self.set_next_step("plea", skip=["company_details",
                                             "company_finances"])

        return clean_data


class PleaStage(FormStage):
    name = "plea"
    template = "plea.html"
    form_class = PleaForm
    dependencies = ["case", "your_details", "company_details"]

    def get_offences(self, urn):
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

    def load_forms(self, data=None, initial=False):
        urn = self.all_data["case"].get("urn")
        # TODO: change this to grabbing by case OU or a FK at some point
        offences = self.get_offences(urn)

        forms_wanted = self.all_data["case"].get("number_of_charges", 1)
        if offences:
            forms_wanted = len(offences)
            self.all_data["case"]["number_of_charges"] = forms_wanted

        if data:
            data["form-TOTAL_FORMS"] = forms_wanted
            data["form-MAX_NUM_FORMS"] = forms_wanted

        extra_forms = 0
        # truncate forms data if the count has changed
        if "PleaForms" in self.all_data["plea"]:
            forms_count = len(self.all_data["plea"]["PleaForms"])
            # truncate data if the count is changed
            if forms_count > forms_wanted:
                self.all_data["plea"]["PleaForms"] = self.all_data["plea"]["PleaForms"][:forms_wanted]
                forms_count = forms_wanted

            if forms_count < forms_wanted:
                self.all_data["plea"].pop("split_form", None)
                extra_forms = forms_wanted - forms_count

        else:
            extra_forms = forms_wanted

        PleaForms = formset_factory(PleaForm, formset=RequiredFormSet, extra=extra_forms, max_num=forms_wanted)

        if initial:
            initial_plea_data = self.all_data[self.name].get("PleaForms", [])
            self.form = PleaForms(initial=initial_plea_data)
        else:
            self.form = PleaForms(data)

        if offences:
            for idx, plea_form in enumerate(self.form.forms):
                try:
                    plea_form.case_data = offences[idx]
                except IndexError:
                    pass

        formset_has_errors = False
        if self.form.errors:
            for error in self.form.errors:
                if error:
                    formset_has_errors = True

        self.context["formset_has_errors"] = formset_has_errors

    def save_forms(self):
        form_data = {}
        urn = self.all_data["case"].get("urn")

        if hasattr(self.form, "management_form"):
            form_data["PleaForms"] = self.form.cleaned_data
        else:
            form_data.update(self.form.cleaned_data)

        # TODO: change this to grabbing by case OU or a FK at some point
        offences = self.get_offences(urn)

        if offences:
            for idx, plea_data in enumerate(form_data["PleaForms"]):
                try:
                    plea_data["title"] = offences[idx].offence_short_title
                except IndexError:
                    pass

        return form_data

    def save(self, form_data, next_step=None):
        clean_data = super(PleaStage, self).save(form_data, next_step)

        none_guilty = True
        if "PleaForms" in clean_data:
            for form in clean_data["PleaForms"]:
                if form["guilty"] == "guilty":
                    none_guilty = False
        else:
            return clean_data

        if self.split_form is None or self.split_form == "split_form_last_step":
            if self.all_data["case"].get("plea_made_by", "Defendant") == "Company representative":
                if none_guilty:
                    self.set_next_step("review", skip=["company_finances",
                                                       "your_finances"])
                else:
                    self.set_next_step("company_finances", skip=["your_finances"])
            else:
                # determine if your_finances needs to be loaded
                if none_guilty:
                    self.all_data["your_finances"]["complete"] = True
                    self.all_data["your_finances"]["skipped"] = True
                    self.set_next_step("review")
                elif "skipped" in self.all_data["your_finances"]:
                    del self.all_data["your_finances"]["skipped"]

        return clean_data


class CompanyFinancesStage(FormStage):
    name = "company_finances"
    template = "company_finances.html"
    form_class = CompanyFinancesForm
    dependencies = ["case"]


class YourMoneyStage(FormStage):
    name = "your_finances"
    template = "your_finances.html"
    form_class = YourMoneyForm
    dependencies = ["case", "your_details", "plea"]

    def save(self, form_data, next_step=None):

        clean_data = super(YourMoneyStage, self).save(form_data, next_step)

        you_are = clean_data.get("you_are", None)

        if self.split_form is None or self.split_form == "split_form_last_step":
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
    dependencies = ["case", "your_details", "plea", "your_finances"]


class HouseholdExpensesStage(FormStage):
    name = "household_expenses"
    template = "household_expenses.html"
    form_class = HouseholdExpensesForm
    dependencies = ["case", "your_details", "plea", "your_finances", "hardship"]

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
    dependencies = ["case", "your_details", "plea", "your_finances", "hardship", "household_expenses"]

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
    dependencies = ["case", "company_details", "your_details", "plea",
                    "your_finances", "company_finances"]

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
    dependencies = ["case", "your_details", "company_details", "plea",
                    "your_finances", "company_finances", "review"]

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
