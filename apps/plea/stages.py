from dateutil.parser import parse
import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory

from apps.govuk_utils.forms import FormStage
from email import send_plea_email
from forms import (CaseForm, YourDetailsForm, YourMoneyForm,
                   PleaForm, ConfirmationForm, RequiredFormSet,
                   YourExpensesForm)

from .fields import ERROR_MESSAGES


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


class CaseStage(FormStage):
    name = "case"
    template = "plea/case.html"
    form_classes = [CaseForm, ]
    dependencies = []

    def render(self, request_context):
        if 'urn' in self.forms[0].errors and ERROR_MESSAGES['URN_ALREADY_USED'] in self.forms[0].errors['urn']:

            self.context['urn_already_used'] = True

        return super(CaseStage, self).render(request_context)


class YourDetailsStage(FormStage):
    name = "your_details"
    template = "plea/about.html"
    form_classes = [YourDetailsForm]
    dependencies = ["case"]


class PleaStage(FormStage):
    name = "plea"
    template = "plea/plea.html"
    form_classes = [PleaForm, ]
    dependencies = ["case", "your_details"]

    def load_forms(self, data=None, initial=False):
        forms_wanted = self.all_data["case"].get("number_of_charges", 1)
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
                extra_forms = forms_wanted - forms_count

        else:
            extra_forms = forms_wanted

        PleaForms = formset_factory(PleaForm, formset=RequiredFormSet, extra=extra_forms, max_num=forms_wanted)

        if initial:
            initial_plea_data = self.all_data[self.name].get("PleaForms", [])
            self.forms.append(PleaForms(initial=initial_plea_data))
        else:
            self.forms.append(PleaForms(data))

        for form in self.forms:
            if form.errors:
                self.context["formset_has_errors"] = True

    def save_forms(self):
        form_data = {}

        for form in self.forms:
            if hasattr(form, "management_form"):
                form_data["PleaForms"] = form.cleaned_data
            else:
                form_data.update(form.cleaned_data)

        return form_data

    def save(self, form_data, next_step=None):

        clean_data = super(PleaStage, self).save(form_data, next_step)

        none_guilty = True
        if "PleaForms" in clean_data:
            for form in clean_data["PleaForms"]:
                if form["guilty"] == "guilty":
                    none_guilty = False

        if none_guilty:
            self.all_data["your_money"]["complete"] = True
            self.all_data["your_money"]["skipped"] = True
            self.next_step = self.all_urls["review"]
        elif "skipped" in self.all_data["your_money"]:
            del self.all_data["your_money"]["skipped"]

        return clean_data


class YourMoneyStage(FormStage):
    name = "your_money"
    template = "plea/your_money.html"
    form_classes = [YourMoneyForm]
    dependencies = ["case", "your_details", "plea"]

    def save(self, form_data, next_step=None):

        clean_data = super(YourMoneyStage, self).save(form_data, next_step)

        if not clean_data.get('hardship', False):
            self.next_step = self.all_urls['review']
            self.all_data["your_expenses"]["complete"] = True

        return clean_data


class YourExpensesStage(FormStage):
    name = "your_expenses"
    template = "plea/your_expenses.html"
    form_classes = [YourExpensesForm]
    dependencies = ["case", "your_details", "plea", "your_money"]

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
            total_household = sum(clean_data[field] for field in household_expense_fields)
            total_other = sum(clean_data[field] for field in other_expense_fields)
            total_expenses = total_household + total_other

            clean_data['total_household_expenses'] = total_household
            clean_data['total_other_expenses'] = total_other
            clean_data['total_expenses'] = total_expenses

        return clean_data


class ReviewStage(FormStage):
    name = "review"
    template = "plea/review.html"
    form_classes = [ConfirmationForm, ]
    dependencies = ["case", "your_details", "plea", "your_money"]

    def save(self, form_data, next_step=None):
        clean_data = super(ReviewStage, self).save(form_data, next_step)

        send_user_email = bool(clean_data.get('receive_email', False))

        if clean_data.get("complete", False):
            email_result = send_plea_email(self.all_data, send_user_email=send_user_email)
            if email_result:
                next_step = reverse_lazy("plea_form_step", args=("complete", ))
            else:
                self.add_message(messages.ERROR, "<h2>Submission Error</h2>Oops there seems to have been a problem submitting your plea. Please try again.")
                next_step = reverse_lazy('plea_form_step', args=('review', ))

            self.next_step = next_step

        return clean_data


class CompleteStage(FormStage):
    name = "complete"
    template = "plea/complete.html"
    form_classes = []
    dependencies = ["case", "your_details", "plea", "your_money", "review"]

    def render(self, request_context):

        request_context['plea_type'] = get_plea_type(self.all_data)

        if isinstance(self.all_data["case"]["date_of_hearing"], basestring):
            court_date = parse(self.all_data["case"]["date_of_hearing"])
        else:
            court_date = self.all_data["case"]["date_of_hearing"]
        request_context["days_before_hearing"] = (court_date - datetime.datetime.today()).days
        request_context["will_hear_by"] = court_date + datetime.timedelta(days=3)

        return super(CompleteStage, self).render(request_context)

