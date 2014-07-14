import smtplib
import socket

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import MultiWidget
from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.forms.widgets import Textarea, RadioSelect

from manchester_traffic_offences.apps.govuk_utils.forms import \
    GovUkDateWidget, FormStage, MultiStageForm
from manchester_traffic_offences.apps.defendant.utils import is_valid_urn_format
from email import send_plea_email


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class URNWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.NumberInput(attrs={'maxlength': '2'}),
                   forms.TextInput(attrs={'maxlength': '7'}),
                   forms.NumberInput(attrs={'maxlength': '2'}),
                   forms.NumberInput(attrs={'maxlength': '2'}),
                   ]
        super(URNWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split('/')
        else:
            return ['', '', '', '']

    def format_output(self, rendered_widgets):
        return '/'.join(rendered_widgets)


class URNField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
            list_fields = [forms.fields.CharField(max_length=2),
                           forms.fields.CharField(max_length=2),
                           forms.fields.CharField(max_length=7),
                           forms.fields.CharField(max_length=2)]
            super(URNField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        return "/".join(values)

    default_validators = [is_valid_urn_format, ]
    widget = URNWidget()


class BasePleaStepForm(forms.Form):
    """
    Note that names in these forms can't be the same, otherwise they will get
    merged in to the last value used.
    """
    pass


class AboutForm(BasePleaStepForm):
    date_of_hearing = forms.DateField(widget=GovUkDateWidget())
    urn = URNField(required=True)
    name = forms.CharField(max_length=255, required=True)
    number_of_charges = forms.IntegerField(
        widget=forms.Select(choices=[(i, i) for i in range(1, 11)]))


class PleaInfoForm(BasePleaStepForm):
    understand = forms.BooleanField(required=True)


class PleaForm(BasePleaStepForm):
    PLEA_CHOICES = (
        ('guilty', 'Guilty'),
        ('not_guilty', 'Not Guilty'),
    )

    guilty = forms.ChoiceField(
        choices=PLEA_CHOICES, widget=RadioSelect(), required=True)
    mitigations = forms.CharField(widget=Textarea(), required=False)


###### Form stage classes #######

class AboutStage(FormStage):
    name = "about"
    template = "plea/about.html"
    form_classes = [AboutForm, ]


class PleaStage(FormStage):
    name = "plea"
    template = "plea/plea.html"
    form_classes = [PleaInfoForm, PleaForm]

    def load_forms(self, data=None, initial=False):
        forms_wanted = self.all_data["about"].get("number_of_charges", 1)
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

        PleaForms = formset_factory(PleaForm, formset=RequiredFormSet, extra=extra_forms)

        if initial:
            initial_plea_data = self.all_data[self.name].get("PleaForms", [])
            initial_info_data = self.all_data[self.name]
            self.forms.append(PleaInfoForm(initial=initial_info_data))
            self.forms.append(PleaForms(initial=initial_plea_data))
        else:
            self.forms.append(PleaInfoForm(data))
            self.forms.append(PleaForms(data))

    def save_forms(self):
        form_data = {}

        for form in self.forms:
            if hasattr(form, "management_form"):
                form_data["PleaForms"] = form.cleaned_data
            else:
                form_data.update(form.cleaned_data)

        return form_data


class ReviewStage(FormStage):
    name = "review"
    template = "plea/review.html"
    form_classes = []

    def save(self, form_data, next=None):
        response = super(ReviewStage, self).save(form_data)

        try:
            send_plea_email(self.all_data)
            next_step = reverse_lazy("plea_form_step", args=("complete", ))
        except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
            next_step = reverse_lazy(
                'plea_form_step', args=('review_send_error', ))

        self.next = next_step
        return form_data


class ReviewSendErrorStage(FormStage):
    name = "send_error"
    template = "plea/review_send_error.html"
    form_classes = []


class CompleteStage(FormStage):
    name = "complete"
    template = "plea/complete.html"
    form_classes = []


class PleaOnlineForms(MultiStageForm):
    stage_classes = [AboutStage,
                     PleaStage,
                     ReviewStage,
                     ReviewSendErrorStage,
                     CompleteStage]
