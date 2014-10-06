from __future__ import unicode_literals

from django import forms
from django.forms.widgets import Textarea, RadioSelect
from .fields import (ERROR_MESSAGES, is_date_in_future, DSRadioFieldRenderer,
                     RequiredFormSet,
                     URNField, HearingTimeField, MoneyField,
                     HearingDateWidget, MoneyFieldWidget)


class BasePleaStepForm(forms.Form):
    pass


class CaseForm(BasePleaStepForm):
    urn = URNField(label="Unique reference number (URN)",
                   required=True, help_text="On page 1 of the pack, in the top right corner",
                   error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"]})
    date_of_hearing = forms.DateField(widget=HearingDateWidget, validators=[is_date_in_future],
                                      help_text="On page 1 of the pack, near the top on the left<br>For example, 30/07/2014",
                                      error_messages={"required": ERROR_MESSAGES["HEARING_DATE_REQUIRED"],
                                                      "invalid": ERROR_MESSAGES["HEARING_DATE_INVALID"]})
    time_of_hearing = HearingTimeField(label="Time",
                                       error_messages={"required": ERROR_MESSAGES["HEARING_TIME_REQUIRED"],
                                                       "invalid": ERROR_MESSAGES["HEARING_DATE_INVALID"]})
    number_of_charges = forms.IntegerField(label="Number of charges against you",
                                           widget=forms.TextInput(attrs={"maxlength": "7", "pattern": "[0-9]+"}),
                                           help_text="On page 2 of the pack, in numbered boxes.<br>For example, 1",
                                           min_value=1, max_value=10,
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
    YOU_ARE_CHOICES = (("employed", "Employed"),
                       ("self employed", "Self employed"),
                       ("receiving benefits", "Receiving benefits"),
                       ("other", "Other"))
    you_are = forms.ChoiceField(label="Are you", choices=YOU_ARE_CHOICES,
                                widget=forms.RadioSelect(renderer=DSRadioFieldRenderer),
                                error_messages={"required": ERROR_MESSAGES["YOU_ARE_REQUIRED"]})
    employer_name = forms.CharField(required=False, max_length=100, label="Employer's name",
                                    error_messages={"required": ERROR_MESSAGES["EMPLOYERS_NAME_REQUIRED"]})
    employer_address = forms.CharField(required=False, max_length=500, label="Employer's full address",
                                       widget=forms.Textarea, error_messages={"required": ERROR_MESSAGES["EMPLOYERS_ADDRESS_REQUIRED"]})
    employer_phone = forms.CharField(required=False, max_length=100, label="Employer's phone",
                                     error_messages={"required": ERROR_MESSAGES["EMPLOYERS_PHONE_REQUIRED"]})
    take_home_pay = MoneyField(required=False, label="Your take home pay (after tax)",
                               error_messages={"required": ERROR_MESSAGES["PAY_REQUIRED"],
                                               "incomplete": ERROR_MESSAGES["PAY_REQUIRED"]})

    your_job = forms.CharField(required=False, max_length=100, label="What's your job?",
                               error_messages={"required": ERROR_MESSAGES["YOUR_JOB_REQUIRED"]})
    self_employed_pay = MoneyField(required=False, label="Your take home pay",
                                   widget=MoneyFieldWidget(amount_label="What is your average take home pay?"),
                                   error_messages={"required": ERROR_MESSAGES["PAY_REQUIRED"],
                                   "incomplete": ERROR_MESSAGES["SELF_EMPLOYED_PAY_REQUIRED"]})

    benefits = MoneyField(required=False, label="Total benefits",
                          widget=MoneyFieldWidget(amount_label="Total benefits", period_label="When do you get your benefits paid?"),
                          error_messages={"required": ERROR_MESSAGES["BENEFITS_REQUIRED"],
                                          "incomplete": ERROR_MESSAGES["BENEFITS_REQUIRED"]})

    other_info = forms.CharField(required=False, max_length=500, label="", help_text="Please provide additional information",
                                 widget=forms.Textarea, error_messages={"required": ERROR_MESSAGES["OTHER_INFO_REQUIRED"]})

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

            if data["you_are"] == "self employed":
                self.fields["your_job"].required = True
                self.fields["self_employed_pay"].required = True

            if data["you_are"] == "receiving benefits":
                    self.fields["benefits"].required = True

            if data["you_are"] == "other":
                self.fields["other_info"].required = True


class ConfirmationForm(BasePleaStepForm):
    understand = forms.BooleanField(required=True,
                                    error_messages={"required": ERROR_MESSAGES["UNDERSTAND_REQUIRED"]})


class PleaForm(BasePleaStepForm):
    PLEA_CHOICES = (
        ('guilty', 'Guilty'),
        ('not_guilty', 'Not Guilty'),
    )

    guilty = forms.ChoiceField(choices=PLEA_CHOICES, widget=RadioSelect(), required=True,
                               error_messages={"required": ERROR_MESSAGES["PLEA_REQUIRED"]})
    mitigations = forms.CharField(max_length=5000, widget=Textarea(), required=False)


###### Form stage classes #######

