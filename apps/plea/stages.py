from dateutil.parser import parse
import datetime

from django.contrib import messages
from django.forms.formsets import formset_factory
from django.http import QueryDict
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from apps.govuk_utils.stages import FormStage
from email import send_plea_email
from forms import (CaseForm, YourDetailsForm, CompanyDetailsForm,
                   PleaForm, YourMoneyForm, YourExpensesForm,
                   CompanyFinancesForm, ConfirmationForm, RequiredFormSet)

from .fields import ERROR_MESSAGES
from .models import Court, Case, Offence


def get_plea_type(context_data):
    """
    Determine if pleas for a submission are
        all guilty  - returns "guilty"
        all not guilty - returns "not_guilty"
        or mixed - returns "mixed"
    """

    guilty_count = len([plea for plea in context_data['plea']['PleaForms']
                        if plea['guilty'] == "guilty"])

    if guilty_count == 0:
        return "not_guilty"
    elif guilty_count == len(context_data['plea']['PleaForms']):
        return "guilty"
    else:
        return "mixed"

def get_case(urn):
    try:
        return Case.objects.get(urn__iexact=urn, sent=False)
    except Case.DoesNotExist:
        return None


class CaseStage(FormStage):
    name = "case"
    template = "plea/case.html"
    form_class = CaseForm
    dependencies = []

    def render(self, request_context):
        if 'urn' in self.form.errors and ERROR_MESSAGES['URN_ALREADY_USED'] in self.form.errors['urn']:
            self.context['urn_already_used'] = True

            try:
                self.context["court"] = Court.objects.get_by_urn(
                    self.form.data['urn_0'])
            except Court.DoesNotExist:
                pass

        return super(CaseStage, self).render(request_context)

    def save(self, form_data, next_step=None):
        clean_data = super(CaseStage, self).save(form_data, next_step)

        if 'complete' in clean_data:
            if clean_data.get("plea_made_by", "Defendant") == "Defendant":
                self.set_next_step("your_details")
            else:
                self.set_next_step("company_details")

        return clean_data


class CompanyDetailsStage(FormStage):
    name = "company_details"
    template = "plea/company_details.html"
    form_class = CompanyDetailsForm
    dependencies = ["case"]

    def save(self, form_data, next_step=None):
        clean_data = super(CompanyDetailsStage,
                           self).save(form_data, next_step)

        if 'complete' in clean_data:
            self.set_next_step("plea", skip=["your_details", "your_finances",
                                             "your_expenses"])

        return clean_data


class YourDetailsStage(FormStage):
    name = "your_details"
    template = "plea/your_details.html"
    form_class = YourDetailsForm
    dependencies = ["case"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourDetailsStage,
                           self).save(form_data, next_step)

        if 'complete' in clean_data:
            self.set_next_step("plea", skip=["company_details",
                                             "company_finances"])

        return clean_data


class PleaStage(FormStage):
    name = "plea"
    template = "plea/plea.html"
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
                    select={'seq_number': "cast(coalesce(nullif(offence_seq_number,''),'0') as float)"}
                ).order_by('seq_number', "id")

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
                self.all_data["plea"].pop("nojs", None)
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

        if self.nojs is None or self.nojs == "nojs_last_step":
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
    template = "plea/company_finances.html"
    form_class = CompanyFinancesForm
    dependencies = ["case"]


class YourMoneyStage(FormStage):
    name = "your_finances"
    template = "plea/your_finances.html"
    form_class = YourMoneyForm
    dependencies = ["case", "your_details", "plea"]

    def save(self, form_data, next_step=None):

        clean_data = super(YourMoneyStage, self).save(form_data, next_step)

        you_are = clean_data.get('you_are', None)

        if self.nojs is None or self.nojs == "nojs_last_step":
            if you_are:
                hardship_field = you_are.replace(' ', '_').replace('-', '_').lower() + "_hardship"

                hardship = clean_data.get(hardship_field, False)

                self.all_data["your_finances"]["hardship"] = hardship

                if not hardship:
                    self.set_next_step("review", skip=["your_expenses"])

        return clean_data


class YourExpensesStage(FormStage):
    name = "your_expenses"
    template = "plea/your_expenses.html"
    form_class = YourExpensesForm
    dependencies = ["case", "your_details", "plea", "your_finances"]

    def save(self, form_data, next_step=None):

        household_expense_fields = ['household_accommodation',
                                    'household_utility_bills',
                                    'household_insurance',
                                    'household_council_tax']

        other_expense_fields = ['other_tv_subscription',
                                'other_travel_expenses',
                                'other_telephone',
                                'other_loan_repayments',
                                'other_court_payments',
                                'other_child_maintenance']

        clean_data = super(YourExpensesStage, self).save(form_data, next_step)

        if 'complete' in clean_data:

            self.set_next_step("review", skip=["company_finances"])

            total_household = sum(int(clean_data[field] or 0) for field in household_expense_fields)
            total_other = sum(int(clean_data[field] or 0) for field in other_expense_fields)
            total_expenses = total_household + total_other

            clean_data['total_household_expenses'] = total_household
            clean_data['total_other_expenses'] = total_other
            clean_data['total_expenses'] = total_expenses

        return clean_data


class ReviewStage(FormStage):
    name = "review"
    template = "plea/review.html"
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
            email_result = send_plea_email(self.all_data)
            if email_result:
                self.set_next_step("complete")
            else:
                self.add_message(messages.ERROR, '<h2 class="heading-medium">{}</h2><p>{}</p>'.format(
                    _('Submission Error'),
                    _('There seems to have been a problem submitting your plea. Please try again.')))
                self.set_next_step("review")

        return clean_data


class CompleteStage(FormStage):
    name = "complete"
    template = "plea/complete.html"
    form_class = None
    dependencies = ["case", "your_details", "company_details", "plea",
                    "your_finances", "company_finances", "review"]

    def render(self, request_context):

        self.context['plea_type'] = get_plea_type(self.all_data)

        try:
            self.context["court"] = Court.objects.get_by_urn(
                self.all_data["case"]["urn"])
        except Court.DoesNotExist:
            pass

        if isinstance(self.all_data["case"]["date_of_hearing"], basestring):
            court_date = parse(self.all_data["case"]["date_of_hearing"])
        else:
            court_date = self.all_data["case"]["date_of_hearing"]

        request_context["days_before_hearing"] = (court_date - datetime.datetime.today()).days
        request_context["will_hear_by"] = court_date + datetime.timedelta(days=3)

        return super(CompleteStage, self).render(request_context)

