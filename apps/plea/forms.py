from __future__ import unicode_literals

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import Textarea, RadioSelect
from django.conf import settings

from .fields import (ERROR_MESSAGES, is_date_in_future, is_date_within_range,
                     DSRadioFieldRenderer, 
                     DSStackedRadioFieldRenderer,
                     URNField,
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
                   required=True,
                   help_text="On page 1 of the pack, in the top right corner",
                   error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"]},
                   validators=[is_urn_not_used])

    date_of_hearing = forms.DateField(label="Court hearing date", widget=HearingDateWidget, validators=[is_date_in_future, is_date_within_range],
                                      required=True,
                                      help_text="On page 1 of the pack, near the top on the left.<br>For example, 30/07/2014",
                                      error_messages={"required": ERROR_MESSAGES["HEARING_DATE_REQUIRED"],
                                                      "invalid": ERROR_MESSAGES["HEARING_DATE_INVALID"]})

    number_of_charges = forms.IntegerField(label="Number of charges against you",
                                           widget=forms.TextInput(attrs={"maxlength": "7", "pattern": "[0-9]+", "class": "form-control-inline", "size": "2"}),
                                           help_text="On page 2 of the pack, in numbered boxes.<br>For example, 1",
                                           min_value=1, max_value=10,
                                           error_messages={"required": ERROR_MESSAGES["NUMBER_OF_CHARGES_REQUIRED"]})

    company_plea = forms.TypedChoiceField(required=True, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                          coerce=to_bool,
                                          choices=YESNO_CHOICES,
                                          label="Are you making a plea on behalf of a company?")


class YourDetailsForm(BasePleaStepForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                           max_length=100, required=True, label="Full name",
                           help_text="On page 1 of the pack we sent you",
                           error_messages={"required": ERROR_MESSAGES["FULL_NAME_REQUIRED"]})
    contact_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                     max_length=30, required=True, label="Contact number",
                                     help_text="Home or mobile number.",
                                     error_messages={"required": ERROR_MESSAGES["CONTACT_NUMBER_REQUIRED"],
                                                     "invalid": ERROR_MESSAGES["CONTACT_NUMBER_INVALID"]})
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control"}),
                             required=getattr(settings, "EMAIL_REQUIRED", True), 
                             label="Email",
                             error_messages={"required": ERROR_MESSAGES["EMAIL_ADDRESS_REQUIRED"],
                                             "invalid": ERROR_MESSAGES["EMAIL_ADDRESS_INVALID"]})

class CompanyDetailsForm(BasePleaStepForm):
    COMPANY_POSITION_CHOICES = (
        ("director", "a director"),
        ("company_secretary", "company secretary"),
        ("solicitor", "the company's solicitor"))

    company_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        max_length=100, required=True, label="Company name",
        help_text="As written on page 1 of the pack we sent you.",
        error_messages={"required": ERROR_MESSAGES["FULL_NAME_REQUIRED"]})

    company_address = forms.CharField(label="Company address", widget=Textarea())

    your_name = forms.CharField(label="Your name",
                                widget=forms.TextInput(attrs={"class": "form-control"}),
                                required=True)

    position_in_company = forms.ChoiceField(choices=COMPANY_POSITION_CHOICES,
                                            widget=RadioSelect(renderer=DSStackedRadioFieldRenderer),
                                            help_text="You must confirm that you are:")

    contact_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                     max_length=30, required=True, label="Contact number",
                                     help_text="Home or mobile number.",
                                     error_messages={"required": ERROR_MESSAGES["CONTACT_NUMBER_REQUIRED"],
                                                     "invalid": ERROR_MESSAGES["CONTACT_NUMBER_INVALID"]})
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control"}),
                             required=getattr(settings, "EMAIL_REQUIRED", True),
                             label="Email",
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
                         ("Self-employed other", "Other"),)
    BEN_PERIOD_CHOICES = (("Weekly", "Weekly"),
                         ("Fortnightly", "Fortnightly"),
                         ("Monthly", "Monthly"),
                         ("Benefits other", "Other"),)
    YES_NO = (("Yes", "Yes"),
              ("No", "No"))

    you_are = forms.ChoiceField(label="Are you?", choices=YOU_ARE_CHOICES,
                                widget=forms.RadioSelect(renderer=DSRadioFieldRenderer),
                                error_messages={"required": ERROR_MESSAGES["YOU_ARE_REQUIRED"]})
    # Employed
    employed_your_job = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                        required=False, max_length=500, label="What's your job?",
                                        error_messages={"required": ERROR_MESSAGES["YOUR_JOB_REQUIRED"]})

    employed_take_home_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                      choices=PERIOD_CHOICES, required=False,
                                                      label="How often do you get paid?",
                                                      error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                      "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    employed_take_home_pay_amount = forms.CharField(label="What's your take home pay (after tax)?", required=False,
                                                    widget=forms.TextInput(attrs={"maxlength": "7",
                                                                                  "data-template-trigger": "employed_take_home_pay_period",
                                                                                  "data-template": "What's your {value} take home pay (after tax)?",
                                                                                  "data-template-delegate": "[for=id_employed_take_home_pay_amount]",
                                                                                  "size": "10",
                                                                                  "class": "form-control-inline js-TemplatedElement"}),
                                                    error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                                    "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    employed_hardship = forms.TypedChoiceField(label="Would paying a fine cause you serious financial problems?",
                                               help_text="For example, you would become homeless",
                                               widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                               choices=YESNO_CHOICES,
                                               coerce=to_bool,
                                               required=False)

    # Self employed
    your_job = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                               required=False, max_length=100, label="What's your job?",
                               error_messages={"required": ERROR_MESSAGES["YOUR_JOB_REQUIRED"]})
    self_employed_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                 choices=SE_PERIOD_CHOICES, required=False,
                                                 label="How often do you get paid?",
                                                 error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                 "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    self_employed_pay_amount = forms.CharField(label="What's your average take home pay?", required=False,
                                               widget=forms.TextInput(attrs={"maxlength": "7",
                                                                             "data-template-trigger": "self_employed_pay_period",
                                                                             "data-template": "What's your average {value} take home pay?",
                                                                             "data-template-defaults-for": "Self-employed other",
                                                                             "data-template-delegate": "[for=id_self_employed_pay_amount]",
                                                                             "size": "10",
                                                                             "class": "form-control-inline js-TemplatedElement"}),
                                               error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                               "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})
    self_employed_pay_other = forms.CharField(required=False, max_length=500, label="",
                                              widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                              help_text="Tell us about how often you get paid")

    self_employed_hardship = forms.TypedChoiceField(label="Would paying a fine cause you serious financial problems?",
                                                    help_text="For example, you would become homeless",
                                                    widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                    choices=YESNO_CHOICES,
                                                    coerce=to_bool,
                                                    required=False)

    # On benefits
    benefits_details = forms.CharField(required=False, max_length=500, label="Which benefits do you receive?",
                                       widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}))
    benefits_dependents = forms.ChoiceField(required=False, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YES_NO,
                                            label="Does this include payment for dependants?")
    benefits_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                        choices=BEN_PERIOD_CHOICES, required=False,
                                        label="How often are your benefits paid?",
                                        error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                        "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})
    benefits_pay_other = forms.CharField(required=False, max_length=500, label="",
                                         widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                         help_text="Tell us about how often you get paid")
    benefits_amount = forms.CharField(label="What's your average take home pay?", required=False,
                                      widget=forms.TextInput(attrs={"maxlength": "7",
                                                                    "data-template-trigger": "benefits_period",
                                                                    "data-template": "What's your average {value} take home pay?",
                                                                    "data-template-defaults-for": "Benefits other",
                                                                    "data-template-delegate": "[for=id_benefits_amount]",
                                                                    "size": "10",
                                                                    "class": "form-control-inline js-TemplatedElement"}),
                                      error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                      "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    receiving_benefits_hardship = forms.TypedChoiceField(label="Would paying a fine cause you serious financial problems?",
                                                         help_text="For example, you would become homeless",
                                                         widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                         choices=YESNO_CHOICES,
                                                         coerce=to_bool,
                                                         required=False)

    # Other
    other_details = forms.CharField(required=False, max_length=500, label="Please provide details",
                                    help_text="eg retired, student etc.",
                                    widget=forms.TextInput(attrs={"class": "form-control"}), 
                                    error_messages={"required": ERROR_MESSAGES["OTHER_INFO_REQUIRED"]})
    other_pay_amount = forms.CharField(label="What is your monthly disposable income?", required=False,
                                       widget=forms.TextInput(attrs={"maxlength": "7", 
                                                                     "size": "10",
                                                                     "class": "form-control-inline"}),
                                       error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                       "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    other_hardship = forms.TypedChoiceField(label="Would paying a fine cause you serious financial problems?",
                                            help_text="For example, you would become homeless",
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
        label="How would paying a fine cause you serious financial problems?",
        help_text="What should the court consider when deciding on any possible fine?",
        widget=forms.Textarea(attrs={'cols': 45, 'rows': 5, "class": "form-control"}),
        required=True,
        error_messages={'required': ERROR_MESSAGES['HARDSHIP_DETAILS_REQUIRED']})

    household_accommodation = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Accommodation",
        help_text="Rent, mortgage or lodgings",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_MIN']})

    household_utility_bills = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Utility bills",
        help_text="Gas, water, electricity etc",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_MIN']})

    household_insurance = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Insurance",
        help_text="Home, life insurance etc",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_MIN']})

    household_council_tax = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Council tax",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_MIN']})

    other_bill_payers = forms.ChoiceField(
        widget=RadioSelect(renderer=DSRadioFieldRenderer),
        label="Does anyone else contribute to these bills?",
        choices=((True, 'Yes'), (False, 'No')),
        error_messages={'required': ERROR_MESSAGES['OTHER_BILL_PAYERS_REQUIRED']})

    other_tv_subscription = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Television subscription",
        help_text="TV licence, satellite etc",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_MIN']})

    other_travel_expenses = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Travel expenses",
        help_text="Fuel, car, public transport etc",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_MIN']})

    other_telephone = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Telephone",
        help_text="Landline and/or mobile",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_TELEPHONE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TELEPHONE_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TELEPHONE_MIN']})

    other_loan_repayments = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Loan repayments",
        help_text="Credit card, bank etc",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_MIN']})

    other_court_payments = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="County court orders",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_MIN']})

    other_child_maintenance = forms.DecimalField(
        initial=0,
        min_value=0,
        decimal_places=2,
        label="Child maintenance",
        widget=forms.TextInput(attrs={"size": "15", "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_MIN']})


class CompanyFinancesForm(BasePleaStepForm):

    trading_period = forms.TypedChoiceField(required=True, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YESNO_CHOICES,
                                            coerce=to_bool,
                                            label="Has the company been trading for more than 12 months?")

    number_of_employees = forms.IntegerField(label="Number of employees",
                                             widget=forms.TextInput(attrs={"maxlength": "7", "pattern": "[0-9]+", "class": "form-control-inline", "size": "2"}),
                                             min_value=1, max_value=10000,
                                             error_messages={"required": ERROR_MESSAGES["NUMBER_OF_CHARGES_REQUIRED"]},
                                             required=False)

    gross_turnover = forms.DecimalField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                        max_digits=10,
                                        decimal_places=2,
                                        help_text="For example, 150000",
                                        initial=0,
                                        required=False)

    net_turnover = forms.DecimalField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                      help_text="For example, 110000",
                                      max_digits=10,
                                      decimal_places=2,
                                      initial=0,
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(CompanyFinancesForm, self).__init__(*args, **kwargs)
        try:
            data = args[0]
        except IndexError:
            data = {}

        if "trading_period" in data:
            self.fields["number_of_employees"].required = True
            self.fields["gross_turnover"].required = True
            self.fields["net_turnover"].required = True


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