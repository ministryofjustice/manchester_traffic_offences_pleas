from __future__ import unicode_literals

from dateutil.parser import parse
import datetime
import six

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import MultiWidget
from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.forms.widgets import Textarea, RadioSelect, NumberInput, RadioFieldRenderer
from django.forms.extras.widgets import Widget
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_text
from django.utils.safestring import mark_safe

from govuk_utils.forms import FormStage, MultiStageForm
from defendant.utils import is_valid_urn_format
from email import send_plea_email


class DSRadioFieldRenderer(RadioFieldRenderer):
    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)

        context = {"id": id_, "renderer": self, "inputs": [force_text(widget) for widget in self]}

        return render_to_string("widgets/RadioSelect.html", context)


class FixedTimeDateWidget(Widget):
    year_field = "%s_year"
    month_field = "%s_month"
    day_field = "%s_day"
    time_field = "%s_time"
    times = [(00, 00, "Midnight"), (12, 00, "Midday")]

    def get_time_choices(self):
        return (("{0}:{1}".format(*time), time[2]) for time in self.times)

    def get_time_from_val(self, val):
        return "{0}:{1}".format(*val)

    def create_input(self, name, field, value, val, **attrs):
        if "id" in self.attrs:
            id_ = self.attrs["id"]
        else:
            id_ = "id_%s" % name

        local_attrs = self.build_attrs(id=field % id_, **attrs)

        i = NumberInput()
        input_html = i.render(field % name, val, local_attrs)
        return input_html

    def create_radio(self, name, field, value, val):
        if "id" in self.attrs:
            id_ = self.attrs["id"]
        else:
            id_ = "id_%s" % name

        local_attrs = self.build_attrs(id=field % id_)

        r = RadioSelect(choices=self.get_time_choices(), renderer=DSRadioFieldRenderer)
        radio_html = r.render(field % name, val, local_attrs)
        return radio_html

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        t = data.get(self.time_field % name)
        if t:
            hr = t.split(":")[0]
            mn = t.split(":")[1]
        else:
            hr, mn = None, None

        if y == m == d == hr == mn == "0":
            return None
        if y and m and d and t:
            datetime_value = datetime.datetime(int(y), int(m), int(d), int(hr), int(mn))
            return str(datetime_value)

        return data.get(name, None)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val, hour_val, minute_val = value.year, value.month, value.day, value.hour, value.minute
        except AttributeError:
            year_val, month_val, day_val, hour_val, minute_val = (None, None, None, None, None)
            if isinstance(value, six.string_types):
                try:
                    v = parse(force_str(value))
                    year_val, month_val, day_val, hour_val, minute_val = v.year, v.month, v.day, v.hour, v.minute
                except ValueError:
                    pass

        year_html = self.create_input(name, self.year_field, value, year_val)
        month_html = self.create_input(name, self.month_field, value, month_val, min=1, max=12)
        day_html = self.create_input(name, self.day_field, value, day_val, min=1, max=31)
        time_html = self.create_radio(name, self.time_field, value, self.get_time_from_val((hour_val, minute_val)))

        context = {"year": year_html, "month": month_html, "day": day_html, "time": time_html}
        return render_to_string("widgets/FixedDateTimeWidget.html", context)


class HearingDateTimeWidget(FixedTimeDateWidget):
    times = [(9, 15, "9:15am"), (13, 15, "1:15pm")]


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class URNWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.NumberInput(attrs={'maxlength': '2'}),
                   forms.TextInput(attrs={'maxlength': '2'}),
                   forms.NumberInput(attrs={'maxlength': '7'}),
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
    date_of_hearing = forms.DateTimeField(widget=HearingDateTimeWidget())
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

        email_result = send_plea_email(self.all_data)
        if email_result:
            next_step = reverse_lazy("plea_form_step", args=("complete", ))

        else:
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

    def render(self, request_context):
        for form_data in self.all_data["plea"]["PleaForms"]:
            if form_data["guilty"] == "guilty":
                request_context["some_guilty"] = True

        return super(CompleteStage, self).render(request_context)


class PleaOnlineForms(MultiStageForm):
    stage_classes = [AboutStage,
                     PleaStage,
                     ReviewStage,
                     ReviewSendErrorStage,
                     CompleteStage]
