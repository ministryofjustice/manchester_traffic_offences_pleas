from __future__ import unicode_literals

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import Textarea, RadioSelect
from django.conf import settings

from .fields import (ERROR_MESSAGES, is_date_in_future, DSRadioFieldRenderer, RadioFieldRenderer,
                     URNField, HearingTimeField,
                     HearingDateWidget, is_urn_not_used)

YESNO_CHOICES = (
    (True, "Yes"),
    (False, "No")
)

to_bool = lambda x: x == "True"


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
    BEN_PERIOD_CHOICES = (("Weekly", "Weekly"),
                         ("Fortnightly", "Fortnightly"),
                         ("Monthly", "Monthly"),
                         ("benefits other", "Other"),)
    YES_NO = (("Yes", "Yes"),
              ("No", "No"))
    you_are = forms.ChoiceField(label="Are you...", choices=YOU_ARE_CHOICES,
                                widget=forms.RadioSelect(renderer=DSRadioFieldRenderer),
                                error_messages={"required": ERROR_MESSAGES["YOU_ARE_REQUIRED"]})
    # Employed
    employed_your_job = forms.CharField(required=False, max_length=500, label="What's your job?",
                                        error_messages={"required": ERROR_MESSAGES["HEARING_DATE_REQUIRED"]})
    employed_take_home_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                      choices=PERIOD_CHOICES, required=False,
                                                      label="How often do you get paid?",
                                                      error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                      "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    employed_take_home_pay_amount = forms.CharField(label="What's your take home pay (after tax)?", required=False,
                                                    widget=forms.TextInput(attrs={"maxlength": "7", "class": "amount",
                                                                                  "data-label-template-value": "employed_take_home_pay_period",
                                                                                  "data-label-template": "What's your {0} take home pay (after tax)?"}),
                                                    error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                                    "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    employed_hardship = forms.TypedChoiceField(label="Would paying a fine cause you financial hardship?",
                                               widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                               choices=YESNO_CHOICES,
                                               coerce=to_bool,
                                               required=False)

    # Self employed
    your_job = forms.CharField(required=False, max_length=100, label="What's your job?",
                               error_messages={"required": ERROR_MESSAGES["YOUR_JOB_REQUIRED"]})
    self_employed_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                 choices=SE_PERIOD_CHOICES, required=False,
                                                 label="How often do you get paid?",
                                                 error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                 "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    self_employed_pay_amount = forms.CharField(label="What's your average take home pay?", required=False,
                                               widget=forms.TextInput(attrs={"maxlength": "7", "class": "amount",
                                                                             "data-label-template-value": "self_employed_pay_period",
                                                                             "data-label-template": "What's your average {0} take home pay?"}),
                                               error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                               "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})
    self_employed_pay_other = forms.CharField(required=False, max_length=500, label="",
                                              widget=forms.Textarea(attrs={"rows": "2"}),
                                              help_text="Tell us about how often you get paid")

    self_employed_hardship = forms.TypedChoiceField(label="Would paying a fine cause you financial hardship?",
                                                    widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                    choices=YESNO_CHOICES,
                                                    coerce=to_bool,
                                                    required=False)

    # On benefits
    benefits_details = forms.CharField(required=False, max_length=500, label="Which benefits do you receive?",
                                       widget=forms.Textarea(attrs={"rows": "2"}))
    benefits_dependents = forms.ChoiceField(required=False, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YES_NO,
                                            label="Does this include payment for dependents?")
    benefits_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                        choices=BEN_PERIOD_CHOICES, required=False,
                                        label="When do you get your benefits paid?",
                                        error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                        "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    benefits_pay_other = forms.CharField(required=False, max_length=500, label="",
                                         widget=forms.Textarea(attrs={"rows": "2"}),
                                         help_text="Tell us about how often you get paid")
    benefits_amount = forms.CharField(label="What's your average take home pay?", required=False,
                                      widget=forms.TextInput(attrs={"maxlength": "7", "class": "amount",
                                                                    "data-label-template-value": "benefits_period",
                                                                    "data-label-template": "What's your average {0} take home pay?"}),
                                      error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                      "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    receiving_benefits_hardship = forms.TypedChoiceField(label="Would paying a fine cause you financial hardship?",
                                                         widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                         choices=YESNO_CHOICES,
                                                         coerce=to_bool,
                                                         required=False)

    # Other
    other_details = forms.CharField(required=False, max_length=500, label="Please provide details e.g. retired, student etc.",
                                    widget=forms.Textarea, error_messages={"required": ERROR_MESSAGES["OTHER_INFO_REQUIRED"]})
    other_pay_amount = forms.CharField(label="What is your monthly disposable income?", required=False,
                                       widget=forms.TextInput(attrs={"maxlength": "7", "class": "amount"}),
                                       error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                       "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    other_hardship = forms.TypedChoiceField(label="Would paying a fine cause you financial hardship?",
                                            widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YESNO_CHOICES,
                                            coerce=to_bool,
                                            required=False)


    def __init__(self, *args, **kwargs):
        super(YourMoneyForm, self).__init__(*args, **kwargs)
        try:
            data = args[0]
        except IndexError:
            data = {}

        if "you_are" in data:
            if data["you_are"] == "Employed":
                self.fields["employed_your_job"].required = True
                self.fields["employed_take_home_pay_period"].required = True
                self.fields["employed_take_home_pay_amount"].required = True
                self.fields["employed_hardship"].required = True

            if data["you_are"] == "Self employed":
                self.fields["your_job"].required = True
                self.fields["self_employed_pay_period"].required = True
                self.fields["self_employed_pay_amount"].required = True
                self.fields["self_employed_hardship"].required = True

            if data["you_are"] == "Receiving benefits":
                self.fields["benefits_details"].required = True
                self.fields["benefits_dependents"].required = True
                self.fields["benefits_period"].required = True
                self.fields["benefits_amount"].required = True
                self.fields["receiving_benefits_hardship"].required = True

            if data["you_are"] == "Other":
                self.fields["other_details"].required = True
                self.fields["other_pay_amount"].required = True
                self.fields["other_hardship"].required = True


class YourExpensesForm(BasePleaStepForm):
    hardship_details = forms.CharField(
        label="How would paying a fine cause you financial hardship?",
        help_text="What you feel the court should consider "
                  "when deciding on any possible fine.",
        widget=forms.Textarea,
        required=True,
        error_messages={'required': ERROR_MESSAGES['HARDSHIP_DETAILS_REQUIRED']})

    household_accommodation = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Accommodation",
        help_text="Rent, mortgage or lodgings",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_MIN']})

    household_utility_bills = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Utility bills",
        help_text="Gas, water, electricity etc",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_MIN']})

    household_insurance = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Insurance",
        help_text="Home, life insurance etc",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_MIN']})

    household_council_tax = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Council tax",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_MIN']})

    other_bill_payers = forms.ChoiceField(
        widget=RadioSelect(renderer=DSRadioFieldRenderer),
        help_text="Does anyone else contribute to these bills?",
        choices=((True, 'Yes'), (False, 'No')),
        error_messages={'required': ERROR_MESSAGES['OTHER_BILL_PAYERS_REQUIRED']})

    other_tv_subscription = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Television subscription",
        help_text="TV licence, satellite etc",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_MIN']})

    other_travel_expenses = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Travel expenses",
        help_text="Fuel, car, public transport etc",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_MIN']})

    other_telephone = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Telephone",
        help_text="inc. mobile",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['OTHER_TELEPHONE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TELEPHONE_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TELEPHONE_MIN']})

    other_loan_repayments = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Loan repayments",
        help_text="Credit card, bank etc",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_MIN']})

    other_court_payments = forms.DecimalField(
        initial=0,
        min_value=0,
        label="County court orders",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_MIN']})

    other_child_maintenance = forms.DecimalField(
        initial=0,
        min_value=0,
        label="Child maintenance",
        widget=forms.TextInput,
        error_messages={'required': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_MIN']})


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

