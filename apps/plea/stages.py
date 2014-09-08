from dateutil.parser import parse
import datetime

from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory

from apps.govuk_utils.forms import FormStage
from email import send_plea_email
from forms import (CaseForm, YourDetailsForm, YourMoneyForm,
                   PleaForm, ConfirmationForm, RequiredFormSet)


class CaseStage(FormStage):
    name = "case"
    template = "plea/case.html"
    form_classes = [CaseForm, ]
    dependencies = []


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


class YourMoneyStage(FormStage):
    name = "your_money"
    template = "plea/your_money.html"
    form_classes = [YourMoneyForm]
    dependencies = ["case", "your_details", "plea"]


class ReviewStage(FormStage):
    name = "review"
    template = "plea/review.html"
    form_classes = [ConfirmationForm, ]
    dependencies = ["case", "your_details", "plea", "your_money"]

    def save(self, form_data, next_step=None):
        clean_data = super(ReviewStage, self).save(form_data, next_step)

        if clean_data.get("complete", False):
            email_result = send_plea_email(self.all_data)
            if email_result:
                next_step = reverse_lazy("plea_form_step", args=("complete", ))
            else:
                next_step = reverse_lazy('plea_form_step', args=('send_error', ))

            self.next_step = next_step

        return clean_data


class ReviewSendErrorStage(FormStage):
    name = "send_error"
    template = "plea/review_send_error.html"
    form_classes = []
    dependencies = ["case", "your_details", "plea", "your_money"]

    def save(self, form_data, next_step=None):
        clean_data = super(ReviewSendErrorStage, self).save(form_data, next_step)

        self.next_step = reverse_lazy("plea_form_step", args=("review", ))

        return clean_data


class CompleteStage(FormStage):
    name = "complete"
    template = "plea/complete.html"
    form_classes = []
    dependencies = ["case", "your_details", "plea", "your_money", "review"]

    def render(self, request_context):
        request_context["some_not_guilty"] = False
        for form_data in self.all_data["plea"]["PleaForms"]:
            if form_data["guilty"] == "not_guilty":
                request_context["some_not_guilty"] = True

        if isinstance(self.all_data["case"]["date_of_hearing"], basestring):
            court_date = parse(self.all_data["case"]["date_of_hearing"])
        else:
            court_date = self.all_data["case"]["date_of_hearing"]
        request_context["days_before_hearing"] = (court_date - datetime.datetime.today()).days
        request_context["will_hear_by"] = court_date + datetime.timedelta(days=3)

        return super(CompleteStage, self).render(request_context)

