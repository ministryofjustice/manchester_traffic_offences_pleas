from __future__ import unicode_literals

from dateutil.parser import parse
import datetime
import re
import six

from django import forms
from django.core import exceptions
from django.forms.formsets import BaseFormSet
from django.forms.widgets import (Select, MultiWidget, Textarea, RadioSelect,
                                  TextInput, RadioFieldRenderer)
from django.forms.extras.widgets import Widget
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _


ERROR_MESSAGES = {
    "URN_REQUIRED": "You must enter your unique reference number (URN)",
    "URN_INVALID": "The unique reference number (URN) isn't valid. Enter the number exactly as it appears on page 1 of the pack",
    "HEARING_DATE_REQUIRED": "You must provide the court hearing date ",
    "HEARING_DATE_INVALID": "The court hearing date and/or time isn't a valid format",
    "HEARING_DATE_PASSED": "The court hearing date must be after today",
    "NUMBER_OF_CHARGES_REQUIRED": "You must select the number of charges against you",
    "FULL_NAME_REQUIRED": "Please enter your full name",
    "EMAIL_ADDRESS_REQUIRED": "You must provide an email address",
    "EMAIL_ADDRESS_INVALID": "Email address isn't a valid format",
    "CONTACT_NUMBER_REQUIRED": "You must provide a contact number",
    "CONTACT_NUMBER_INVALID": "The contact number isn't a valid format",
    "PLEA_REQUIRED": "Your plea must be selected",
    "YOU_ARE_REQUIRED": "You must let us know if you're employed, receiving benefits or other",
    "EMPLOYERS_NAME_REQUIRED": "Please enter your employer's full name",
    "EMPLOYERS_ADDRESS_REQUIRED": "You must provide your employer's full address",
    "EMPLOYERS_PHONE_REQUIRED": "Please enter your employer's phone number",
    "PAY_REQUIRED": "Please enter your take home pay and how often you're paid",
    "BENEFITS_REQUIRED": "Please enter total benefits and how often you receive them",
    "UNDERSTAND_REQUIRED": "You must tick the box to confirm the legal statements"
}


def is_valid_urn_format(urn):
    """
    URN is 11 or 13 characters long in the following format:

    00/AA/0000000/00
    or
    00/AA/00000/00
    """

    pattern = r"[0-9]{2}/[a-zA-Z]{2}/(?:[0-9]{5}|[0-9]{7})/[0-9]{2}"

    if not re.match(pattern, urn):
        raise exceptions.ValidationError(_(ERROR_MESSAGES["URN_INVALID"]))

    return True


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

        i = TextInput()
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
        y = data.get(self.year_field % name, None)
        m = data.get(self.month_field % name, None)
        d = data.get(self.day_field % name, None)
        t = data.get(self.time_field % name, None)
        if t:
            hr = t.split(":")[0]
            mn = t.split(":")[1]
        else:
            hr, mn = None, None

        if y == m == d == hr == mn == None:
            return None

        if y and m and d and t:
            try:
                datetime_value = datetime.datetime(int(y), int(m), int(d), int(hr), int(mn))
            except ValueError:
                return "{0}-{1}-{2} {3}:{4}:00".format(y, m, d, hr, mn)
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

        if isinstance(day_val, (int, long, float, complex)):
            day_val = "{num:02d}".format(num=day_val)
        if isinstance(month_val, (int, long, float, complex)):
            month_val = "{num:02d}".format(num=month_val)

        year_html = self.create_input(name, self.year_field, value, year_val,  pattern="[0-9]+", maxlength=4)
        month_html = self.create_input(name, self.month_field, value, month_val, pattern="[0-9]+", maxlength=2)
        day_html = self.create_input(name, self.day_field, value, day_val, pattern="[0-9]+", maxlength=2)
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
        widgets = [forms.TextInput(attrs={'maxlength': '2', 'pattern': '[0-9]+'}),
                   forms.TextInput(attrs={'maxlength': '2'}),
                   forms.TextInput(attrs={'maxlength': '7', 'pattern': '[0-9]+'}),
                   forms.TextInput(attrs={'maxlength': '2', 'pattern': '[0-9]+'}),
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


class MoneyFieldWidget(forms.MultiWidget):
    PERIOD_CHOICES = (("a week", "a week"),
                      ("a fortnight", "a fortnight"),
                      ("a month", "a month"))

    def __init__(self, attrs=None):
        widgets = [TextInput(attrs={'maxlength': '7', 'pattern': '[0-9]+'}),
                   RadioSelect(choices=self.PERIOD_CHOICES)]

        super(MoneyFieldWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(" ", 1)
        else:
            return ["", ""]

    def format_output(self, rendered_widgets):
        return ' '.join(rendered_widgets)


class MoneyField(forms.MultiValueField):
    widget = MoneyFieldWidget()

    def __init__(self, *args, **kwargs):
        list_fields = [forms.CharField(required=False, max_length=7, label="Total benefits"),
                       forms.CharField(required=False)]

        super(MoneyField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, data_list):
        return " ".join(data_list)


class BasePleaStepForm(forms.Form):
    pass


class CaseForm(BasePleaStepForm):
    urn = URNField(required=True, help_text="On page 1 of the pack, in the top right corner",
                   error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"]})
    date_of_hearing = forms.DateTimeField(widget=HearingDateTimeWidget(),
                                          help_text="On page 1 of the pack, near the top on the left<br>For example, 30/07/2014",
                                          error_messages={"required": ERROR_MESSAGES["HEARING_DATE_REQUIRED"],
                                                          "invalid": ERROR_MESSAGES["HEARING_DATE_INVALID"]})
    number_of_charges = forms.IntegerField(
        widget=forms.Select(choices=[("", "Please select ...")] + [(i, i) for i in range(1, 21)]),
        help_text="On page 2 of the pack, in numbered boxes.<br>For example 1",
        error_messages={"required": ERROR_MESSAGES["NUMBER_OF_CHARGES_REQUIRED"]})


class YourDetailsForm(BasePleaStepForm):
    name = forms.CharField(max_length=100, required=True, label="Full name",
                           help_text="On page 1 of the pack we sent you",
                           error_messages={"required": ERROR_MESSAGES["FULL_NAME_REQUIRED"]})
    contact_number = forms.CharField(max_length=30, required=True, label="Contact number",
                                     help_text="Home or mobile number.",
                                     error_messages={"required": ERROR_MESSAGES["CONTACT_NUMBER_REQUIRED"],
                                                     "invalid": ERROR_MESSAGES["CONTACT_NUMBER_INVALID"]})
    email = forms.EmailField(required=True, label="Email", help_text="",
                             error_messages={"required": ERROR_MESSAGES["EMAIL_ADDRESS_REQUIRED"],
                                             "invalid": ERROR_MESSAGES["EMAIL_ADDRESS_INVALID"]})

    national_insurance_number = forms.CharField(max_length=20, label="National Insurance number",
                                                help_text="It's on your National Insurance card, benefit letter, payslip or P60<br>For example, 'QQ 12 34 56 C'.",
                                                required=False)
    driving_licence_number = forms.CharField(max_length=20, label="UK driving licence number",
                                             help_text="Starts with the first five letters from your last name",
                                             required=False)
    registration_number = forms.CharField(max_length=10, label="Registration number",
                                          help_text="Of the vehicle you were driving when charged.",
                                          required=False)


class YourMoneyForm(BasePleaStepForm):
    YOU_ARE_CHOICES = (("employed", "employed"),
                       ("receiving benefits", "receiving benefits"),
                       ("other", "other"))
    you_are = forms.ChoiceField(label="Are you", choices=YOU_ARE_CHOICES,
                                widget=forms.RadioSelect(renderer=DSRadioFieldRenderer),
                                error_messages={"required": ERROR_MESSAGES["YOU_ARE_REQUIRED"]})
    employer_name = forms.CharField(required=False, max_length=100, label="Employer's name",
                                    error_messages={"required": ERROR_MESSAGES["EMPLOYERS_NAME_REQUIRED"]})
    employer_address = forms.CharField(required=False, max_length=500, label="Employer's full address",
                                       widget=forms.Textarea, error_messages={"required": ERROR_MESSAGES["EMPLOYERS_ADDRESS_REQUIRED"]})
    employer_phone = forms.CharField(required=False, max_length=100, label="Employer's phone",
                                     error_messages={"required": ERROR_MESSAGES["EMPLOYERS_PHONE_REQUIRED"]})
    take_home_pay = MoneyField(required=False,
                               error_messages={"required": ERROR_MESSAGES["PAY_REQUIRED"],
                                               "incomplete": ERROR_MESSAGES["PAY_REQUIRED"]})
    benefits = MoneyField(required=False,
                          error_messages={"required": ERROR_MESSAGES["BENEFITS_REQUIRED"],
                                          "incomplete": ERROR_MESSAGES["BENEFITS_REQUIRED"]})

    def __init__(self, *args, **kwargs):
        super(YourMoneyForm, self).__init__(*args, **kwargs)
        try:
            data = args[0]
        except IndexError:
            data = {}

        if "you_are" in data:
            if data["you_are"] == "employed":
                self.fields["employer_name"].required = True
                self.fields["employer_address"].required = True
                self.fields["employer_phone"].required = True
                self.fields["take_home_pay"].required = True

            if data["you_are"] == "receiving benefits":
                    self.fields["benefits"].required = True


class ConfirmationForm(BasePleaStepForm):
    understand = forms.BooleanField(required=True,
                                    error_messages={"required": ERROR_MESSAGES["UNDERSTAND_REQUIRED"]})


class PleaForm(BasePleaStepForm):
    PLEA_CHOICES = (
        ('guilty', 'Guilty'),
        ('not_guilty', 'Not Guilty'),
    )

    guilty = forms.ChoiceField(choices=PLEA_CHOICES, widget=RadioSelect(), required=True,
                               error_messages={"required": "Your plea must be selected"})
    mitigations = forms.CharField(max_length=5000, widget=Textarea(), required=False)


###### Form stage classes #######

