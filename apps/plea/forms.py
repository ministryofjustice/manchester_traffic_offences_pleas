from __future__ import unicode_literals

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import Textarea, RadioSelect
from .fields import (ERROR_MESSAGES, is_date_in_future, DSRadioFieldRenderer, RadioFieldRenderer,
                     URNField, HearingTimeField,
                     HearingDateWidget, is_urn_not_used)


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class BasePleaStepForm(forms.Form):
    pass


class CaseForm(BasePleaStepForm):
    urn = URNField(label="Unique reference number (URN)",
                   required=True, help_text="On page 1 of the pack, in the top right corner",
                   error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"]},
                   validators=[is_urn_not_used])
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
    email = forms.EmailField(required=True, label="Email", help_text="If you choose to we will use this email address for all future correspondence regarding your case, including the court's decision.",
                             error_messages={"required": ERROR_MESSAGES["EMAIL_ADDRESS_REQUIRED"],
                                             "invalid": ERROR_MESSAGES["EMAIL_ADDRESS_INVALID"]})


class YourMoneyForm(BasePleaStepForm):
    YOU_ARE_CHOICES = (("Employed", "Employed"),
                       ("Self employed", "Self employed"),
                       ("Receiving benefits", "Receiving benefits"),
                       ("Other", "Other"))
    PERIOD_CHOICES = (("Weekly", "Weekly"),
                      ("Fortnightly", "Fortnightly"),
                      ("Monthly", "Monthly"))
    SE_PERIOD_CHOICES = (("Weekly", "Weekly"),
                         ("Fortnightly", "Fortnightly"),
                         ("Monthly", "Monthly"),
                         ("self-employed other", "Other"),)
    you_are = forms.ChoiceField(label="Are you", choices=YOU_ARE_CHOICES,
                                widget=forms.RadioSelect(renderer=DSRadioFieldRenderer),
                                error_messages={"required": ERROR_MESSAGES["YOU_ARE_REQUIRED"]})
    # Employed
    employer_name = forms.CharField(required=False, max_length=100, label="Employer's name",
                                    error_messages={"required": ERROR_MESSAGES["EMPLOYERS_NAME_REQUIRED"]})
    employer_address = forms.CharField(required=False, max_length=500, label="Employer's full address",
                                       widget=forms.Textarea, error_messages={"required": ERROR_MESSAGES["EMPLOYERS_ADDRESS_REQUIRED"]})
    employer_phone = forms.CharField(required=False, max_length=100, label="Employer's phone",
                                     error_messages={"required": ERROR_MESSAGES["EMPLOYERS_PHONE_REQUIRED"]})
    take_home_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=RadioFieldRenderer),
                                             choices=PERIOD_CHOICES, required=False,
                                             label="How often do you get paid?",
                                             error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                             "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    take_home_pay_amount = forms.CharField(label="Your take home pay (after tax)", required=False,
                                           widget=forms.TextInput(attrs={"maxlength": "7", "class": "amount"}),
                                           error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                           "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})
    # Self employed
    your_job = forms.CharField(required=False, max_length=100, label="What's your job?",
                               error_messages={"required": ERROR_MESSAGES["YOUR_JOB_REQUIRED"]})
    self_employed_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=RadioFieldRenderer),
                                                 choices=SE_PERIOD_CHOICES, required=False,
                                                 label="How often do you get paid?",
                                                 error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                 "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    self_employed_pay_amount = forms.CharField(label="What is your average take home pay?", required=False,
                                               widget=forms.TextInput(attrs={"maxlength": "7", "class": "amount"}),
                                               error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                               "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})
    self_employed_pay_other = forms.CharField(required=False, max_length=500, label="",
                                              widget=forms.Textarea(attrs={"rows": "2"}),
                                              help_text="Please provide additional information")
    # On benefits
    benefits_period = forms.ChoiceField(widget=RadioSelect(renderer=RadioFieldRenderer),
                                        choices=PERIOD_CHOICES, required=False,
                                        label="When do you get your benefits paid?",
                                        error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                        "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    benefits_amount = forms.CharField(label="Total benefits", required=False,
                                      widget=forms.TextInput(attrs={"maxlength": "7", "class": "amount"}),
                                      error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                      "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    # Other
    other_info = forms.CharField(required=False, max_length=500, label="", help_text="Please provide additional information",
                                 widget=forms.Textarea, error_messages={"required": ERROR_MESSAGES["OTHER_INFO_REQUIRED"]})

    def __init__(self, *args, **kwargs):
        super(YourMoneyForm, self).__init__(*args, **kwargs)
        try:
            data = args[0]
        except IndexError:
            data = {}

        if "you_are" in data:
            if data["you_are"] == "Employed":
                self.fields["employer_name"].required = True
                self.fields["employer_address"].required = True
                self.fields["employer_phone"].required = True
                self.fields["take_home_pay_period"].required = True
                self.fields["take_home_pay_amount"].required = True

            if data["you_are"] == "Self employed":
                self.fields["your_job"].required = True
                self.fields["self_employed_pay_period"].required = True
                self.fields["self_employed_pay_amount"].required = True

            if data["you_are"] == "Receiving benefits":
                self.fields["benefits_period"].required = True
                self.fields["benefits_amount"].required = True

            if data["you_are"] == "Other":
                self.fields["other_info"].required = True


class ConfirmationForm(BasePleaStepForm):
    understand = forms.BooleanField(required=True,
                                    error_messages={"required": ERROR_MESSAGES["UNDERSTAND_REQUIRED"]})

    receive_email = forms.ChoiceField(required=True,
                                      widget=RadioSelect(),
                                      choices=((True, 'Yes'), (False, 'No')),
                                      error_messages={"required": ERROR_MESSAGES["RECEIVE_EMAIL"]})


class PleaForm(BasePleaStepForm):
    PLEA_CHOICES = (
        ('guilty', 'Guilty'),
        ('not_guilty', 'Not Guilty'),
    )

    guilty = forms.ChoiceField(choices=PLEA_CHOICES, widget=RadioSelect(), required=True,
                               error_messages={"required": ERROR_MESSAGES["PLEA_REQUIRED"]})
    mitigations = forms.CharField(max_length=5000, widget=Textarea(), required=False)


###### Form stage classes #######

