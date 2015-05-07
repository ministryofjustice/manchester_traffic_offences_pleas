from __future__ import unicode_literals

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import Textarea, RadioSelect
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .fields import (ERROR_MESSAGES, is_date_in_future, is_date_within_range,
                     DSRadioFieldRenderer, 
                     DSStackedRadioFieldRenderer,
                     URNField,
                     DateWidget, is_urn_not_used, is_urn_valid)

YESNO_CHOICES = (
    (True, _("Yes")),
    (False, _("No"))
)

to_bool = lambda x: x == "True"


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class BasePleaStepForm(forms.Form):
    pass


class NoJSPleaStepForm(BasePleaStepForm):
    nojs = forms.CharField(required=False, widget=forms.HiddenInput)


class CaseForm(BasePleaStepForm):
    PLEA_MADE_BY_CHOICES = (
        ("Defendant", _("The person named on the Postal Requisition")),
        ("Company representative", _("Pleading on behalf of a company")))

    urn = URNField(label=_("Unique reference number (URN)"),
                   required=True,
                   help_text=_("On page 1 of the pack, in the top right corner.<br>For example, 12/AB/34567/00"),
                   error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"]},
                   validators=[is_urn_valid, is_urn_not_used])

    date_of_hearing = forms.DateField(widget=DateWidget,
                                      validators=[is_date_in_future, is_date_within_range],
                                      required=True,
                                      label=_("Court hearing date"),
                                      help_text=_("On page 1 of the pack, near the top on the left.<br>For example, 30/07/2014"),
                                      error_messages={"required": ERROR_MESSAGES["HEARING_DATE_REQUIRED"],
                                                      "invalid": ERROR_MESSAGES["HEARING_DATE_INVALID"]})

    number_of_charges = forms.IntegerField(label=_("Number of charges against you"),
                                           widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                         "maxlength": "2",
                                                                         "class": "form-control-inline"}),
                                           help_text=_("On page 2 of the pack, in numbered boxes.<br>For example, 1"),
                                           min_value=1, max_value=10,
                                           error_messages={"required": ERROR_MESSAGES["NUMBER_OF_CHARGES_REQUIRED"]})

    plea_made_by = forms.TypedChoiceField(required=True, widget=RadioSelect(renderer=DSStackedRadioFieldRenderer),
                                          choices=PLEA_MADE_BY_CHOICES,
                                          label=_("Are you?"),
                                          help_text=_("Choose one of the following options:"),
                                          error_messages={"required": ERROR_MESSAGES["PLEA_MADE_BY_REQUIRED"]})


class YourDetailsForm(BasePleaStepForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                 max_length=100,
                                 required=True,
                                 label=_("First name"),
                                 error_messages={"required": ERROR_MESSAGES["FIRST_NAME_REQUIRED"]})

    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                max_length=100,
                                required=True,
                                label=_("Last name"),
                                error_messages={"required": ERROR_MESSAGES["LAST_NAME_REQUIRED"]})

    correct_address = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                              required=True,
                                              coerce=to_bool,
                                              choices=YESNO_CHOICES,
                                              label=_("Is your address on the Postal Requisition correct?"),
                                              error_messages={"required": ERROR_MESSAGES["CORRECT_ADDRESS_REQUIRED"]})

    updated_address = forms.CharField(widget=forms.Textarea(attrs={"rows": "4", "class": "form-control"}),
                                  required=False,
                                  label="",
                                  help_text=_("If your address is different from the one shown on page 1 of the Postal Requisition, tell us here"),
                                  error_messages={"required": ERROR_MESSAGES["UPDATED_ADDRESS_REQUIRED"]})

    contact_number = forms.CharField(widget=forms.TextInput(attrs={"type": "tel", "class": "form-control"}),
                                     required=True,
                                     max_length=30,
                                     label=_("Contact number"),
                                     help_text=_("Landline or mobile number"),
                                     error_messages={"required": ERROR_MESSAGES["CONTACT_NUMBER_REQUIRED"],
                                                     "invalid": ERROR_MESSAGES["CONTACT_NUMBER_INVALID"]})

    email = forms.EmailField(widget=forms.TextInput(attrs={"type": "email", "class": "form-control"}),
                             required=getattr(settings, "EMAIL_REQUIRED", True), 
                             label=_("Email"),
                             help_text=_("We'll use this for all future correspondence. We'll also contact you by post"),
                             error_messages={"required": ERROR_MESSAGES["EMAIL_ADDRESS_REQUIRED"],
                                             "invalid": ERROR_MESSAGES["EMAIL_ADDRESS_INVALID"]})

    date_of_birth = forms.DateField(widget=DateWidget,
                                    required=True,
                                    label=_("Date of birth"),
                                    error_messages={"required": ERROR_MESSAGES["DATE_OF_BIRTH_REQUIRED"],
                                                    "invalid": ERROR_MESSAGES["DATE_OF_BIRTH_INVALID"]})

    ni_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                required=False,
                                label=_("National Insurance number"),
                                help_text=_("On your National Insurance card, benefit letter, payslip or P60. <br>For example, 'QQ 12 34 56 C'"))

    driving_licence_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                             required=False,
                                             label=_("UK driving licence number"),
                                             help_text=_("Starts with the first five letters from your last name"))

    def __init__(self, *args, **kwargs):
        super(YourDetailsForm, self).__init__(*args, **kwargs)
        try:
            data = args[0]
        except IndexError:
            data = {}

        if "correct_address" in data:
            if data["correct_address"] == "False":
                self.fields["updated_address"].required = True

class CompanyDetailsForm(BasePleaStepForm):
    COMPANY_POSITION_CHOICES = (
        ("Director", _("a director")),
        ("Company secretary", _("the company secretary")),
        ("Company solicitor", _("the company's solicitor")))

    company_name = forms.CharField(label=_("Company name"),
                                   widget=forms.TextInput(attrs={"class": "form-control"}),
                                   max_length=100, 
                                   required=True, 
                                   help_text=_("As written on page 1 of the Postal Requistion we sent you."),
                                   error_messages={"required": ERROR_MESSAGES["COMPANY_NAME_REQUIRED"]})

    company_address = forms.CharField(label=_("Company address"),
                                      widget=Textarea(attrs={"class": "form-control", "rows": "4"}),
                                      help_text=_("This is the address we will use for all future correspondence about this case."),
                                      required=True,
                                      error_messages={"required": ERROR_MESSAGES["COMPANY_ADDRESS_REQUIRED"]})

    first_name = forms.CharField(label=_("Your first name"),
                                 widget=forms.TextInput(attrs={"class": "form-control"}),
                                 required=True,
                                 error_messages={"required": ERROR_MESSAGES["FIRST_NAME_REQUIRED"]})

    last_name = forms.CharField(label=_("Your last name"),
                                 widget=forms.TextInput(attrs={"class": "form-control"}),
                                 required=True,
                                 error_messages={"required": ERROR_MESSAGES["LAST_NAME_REQUIRED"]})

    position_in_company = forms.ChoiceField(label=_("Your position in the company"),
                                            choices=COMPANY_POSITION_CHOICES,
                                            widget=RadioSelect(renderer=DSStackedRadioFieldRenderer),
                                            help_text=_("You must confirm that you are:"),
                                            required=True,
                                            error_messages={"required": ERROR_MESSAGES["POSITION_REQUIRED"]})

    contact_number = forms.CharField(label=_("Contact number"),
                                     widget=forms.TextInput(attrs={"type": "tel", 
                                                                   "class": "form-control"}),
                                     max_length=30,
                                     required=True, 
                                     help_text=_("Office or mobile number."),
                                     error_messages={"required": ERROR_MESSAGES["COMPANY_CONTACT_NUMBER_REQUIRED"],
                                                     "invalid": ERROR_MESSAGES["CONTACT_NUMBER_INVALID"]})

    email = forms.EmailField(widget=forms.TextInput(attrs={"type": "email",
                                                           "class": "form-control"}),
                             required=getattr(settings, "EMAIL_REQUIRED", True),
                             label=_("Email"),
                             error_messages={"required": ERROR_MESSAGES["COMPANY_EMAIL_ADDRESS_REQUIRED"],
                                             "invalid": ERROR_MESSAGES["EMAIL_ADDRESS_INVALID"]})


class YourMoneyForm(BasePleaStepForm):

    YOU_ARE_CHOICES = (("Employed", _("Employed")),
                       ("Self-employed", _("Self-employed")),
                       ("Receiving benefits", _("Receiving benefits")),
                       ("Other", _("Other")))
    PERIOD_CHOICES = (("Weekly", _("Weekly")),
                      ("Fortnightly", _("Fortnightly")),
                      ("Monthly", _("Monthly")))
    SE_PERIOD_CHOICES = (("Weekly", _("Weekly")),
                         ("Fortnightly", _("Fortnightly")),
                         ("Monthly", _("Monthly")),
                         ("Self-employed other", _("Other")),)
    BEN_PERIOD_CHOICES = (("Weekly", _("Weekly")),
                         ("Fortnightly", _("Fortnightly")),
                         ("Monthly", _("Monthly")),
                         ("Benefits other", _("Other")),)
    YES_NO = (("Yes", _("Yes")),
              ("No", _("No")))

    you_are = forms.ChoiceField(label=_("Are you?"), choices=YOU_ARE_CHOICES,
                                widget=forms.RadioSelect(renderer=DSRadioFieldRenderer),
                                error_messages={"required": ERROR_MESSAGES["YOU_ARE_REQUIRED"]})
    # Employed
    employed_take_home_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                      choices=PERIOD_CHOICES, required=False,
                                                      label=_("How often do you get paid?"),
                                                      error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                      "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})

    employed_take_home_pay_amount = forms.DecimalField(label=_("What's your take home pay (after tax)?"), 
                                                       required=False,
                                                       localize=True,
                                                       widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                                     "data-template-trigger": "employed_take_home_pay_period",
                                                                                     "data-template": _("What's your {value} take home pay (after tax)?"),
                                                                                     "data-template-delegate": "[for=id_employed_take_home_pay_amount] .label-text",
                                                                                     "class": "form-control-inline js-TemplatedElement"}),
                                                       error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                                       "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    employed_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                               help_text=_("For example, you would become homeless"),
                                               widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                               choices=YESNO_CHOICES,
                                               coerce=to_bool,
                                               required=False,
                                               error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})

    # Self-employed
    self_employed_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                 choices=SE_PERIOD_CHOICES, required=False,
                                                 label=_("How often do you get paid?"),
                                                 error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                 "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})

    self_employed_pay_amount = forms.DecimalField(label=_("What's your average take home pay?"),
                                                  required=False,
                                                  localize=True,
                                                  widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                                "data-template-trigger": "self_employed_pay_period",
                                                                                "data-template": _("What's your average {value} take home pay?"),
                                                                                "data-template-defaults-for": _("Other"),
                                                                                "data-template-delegate": "[for=id_self_employed_pay_amount] .label-text",
                                                                                "class": "form-control-inline js-TemplatedElement"}),
                                                  error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                                  "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    self_employed_pay_other = forms.CharField(required=False, max_length=500, label="",
                                              widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                              help_text=_("Tell us about how often you get paid"))

    self_employed_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                                    help_text=_("For example, you would become homeless"),
                                                    widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                    choices=YESNO_CHOICES,
                                                    coerce=to_bool,
                                                    required=False,
                                                    error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})

    # On benefits
    benefits_details = forms.CharField(required=False, max_length=500, label=_("Which benefits do you receive?"),
                                       widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                       error_messages={"required": ERROR_MESSAGES["BENEFITS_DETAILS_REQUIRED"]})

    benefits_dependents = forms.ChoiceField(required=False, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YES_NO,
                                            label=_("Does this include payment for dependants?"),
                                            error_messages={"required": ERROR_MESSAGES["BENEFITS_DEPENDANTS_REQUIRED"]})
    
    benefits_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                        choices=BEN_PERIOD_CHOICES, required=False,
                                        label=_("How often are your benefits paid?"),
                                        error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                        "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})

    benefits_pay_other = forms.CharField(required=False, max_length=500, label="",
                                         widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                         help_text=_("Tell us about how often you get paid"))

    benefits_amount = forms.DecimalField(label=_("What's your average take home pay?"),
                                         required=False,
                                         localize=True,
                                         widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                       "data-template-trigger": "benefits_period",
                                                                       "data-template": _("What's your average {value} take home pay?"),
                                                                       "data-template-defaults-for": _("Other"),
                                                                       "data-template-delegate": "[for=id_benefits_amount] .label-text",
                                                                       "class": "form-control-inline js-TemplatedElement"}),
                                         error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                         "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    receiving_benefits_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                                         help_text=_("For example, you would become homeless"),
                                                         widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                         choices=YESNO_CHOICES,
                                                         coerce=to_bool,
                                                         required=False,
                                                         error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})

    # Other
    other_details = forms.CharField(required=False, max_length=500, label=_("Please provide details"),
                                    help_text=_("eg retired, student etc."),
                                    widget=forms.TextInput(attrs={"class": "form-control"}), 
                                    error_messages={"required": ERROR_MESSAGES["OTHER_INFO_REQUIRED"]})

    other_pay_amount = forms.DecimalField(label=_("What is your monthly disposable income?"),
                                          required=False,
                                          localize=True,
                                          widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                        "class": "form-control-inline"}),
                                          error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                          "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    other_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                            help_text=_("For example, you would become homeless"),
                                            widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YESNO_CHOICES,
                                            coerce=to_bool,
                                            required=False,
                                            error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})


    def __init__(self, *args, **kwargs):
        super(YourMoneyForm, self).__init__(*args, **kwargs)
        try:
            data = args[0]
        except IndexError:
            data = {}

        if "you_are" in data:                
            if data["you_are"] == "Employed":
                self.fields["employed_take_home_pay_period"].required = True
                self.fields["employed_take_home_pay_amount"].required = True
                self.fields["employed_hardship"].required = True

            if data["you_are"] == "Self-employed":
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
        label=_("How would paying a fine cause you serious financial problems?"),
        help_text=_("What should the court consider when deciding on any possible fine?"),
        widget=forms.Textarea(attrs={'cols': 45, 'rows': 5, "class": "form-control"}),
        required=True,
        error_messages={'required': ERROR_MESSAGES['HARDSHIP_DETAILS_REQUIRED']})

    household_accommodation = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Accommodation"),
        help_text=_("Rent, mortgage or lodgings"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_ACCOMMODATION_MIN']})

    household_utility_bills = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Utility bills"),
        help_text=_("Gas, water, electricity etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_UTILITY_BILLS_MIN']})

    household_insurance = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Insurance"),
        help_text=_("Home, life insurance etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_MIN']})

    household_council_tax = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Council tax"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['HOUSEHOLD_INSURANCE_MIN']})

    other_bill_payers = forms.ChoiceField(
        widget=RadioSelect(renderer=DSRadioFieldRenderer),
        label=_("Does anyone else contribute to these bills?"),
        choices=((True, _('Yes')), (False, _('No'))),
        error_messages={'required': ERROR_MESSAGES['OTHER_BILL_PAYERS_REQUIRED']})

    other_tv_subscription = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Television subscription"),
        help_text=_("TV licence, satellite etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TV_SUBSCRIPTION_MIN']})

    other_travel_expenses = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Travel expenses"),
        help_text=_("Fuel, car, public transport etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TRAVEL_EXPENSES_MIN']})

    other_telephone = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Telephone"),
        help_text=_("Landline and/or mobile"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_TELEPHONE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_TELEPHONE_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_TELEPHONE_MIN']})

    other_loan_repayments = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Loan repayments"),
        help_text=_("Credit card, bank etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_LOAN_REPAYMENTS_MIN']})

    other_court_payments = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("County court orders"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_COURT_PAYMENTS_MIN']})

    other_child_maintenance = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Child maintenance"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={'required': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_REQUIRED'],
                        'invalid': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_INVALID'],
                        'min_value': ERROR_MESSAGES['OTHER_CHILD_MAINTENANCE_MIN']})


class CompanyFinancesForm(NoJSPleaStepForm):
    dependencies={
        "number_of_employees": {
            "field": "trading_period"
        },
        "gross_turnover": {
            "field": "trading_period"
        },
        "net_turnover": {
            "field": "trading_period"
        }
    }

    trading_period = forms.TypedChoiceField(required=True, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YESNO_CHOICES,
                                            coerce=to_bool,
                                            label=_("Has the company been trading for more than 12 months?"),
                                            error_messages={"required": ERROR_MESSAGES["COMPANY_TRADING_PERIOD"]})

    number_of_employees = forms.IntegerField(label=_("Number of employees"),
                                             widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                          "maxlength": "5",
                                                                           "class": "form-control-inline"}),
                                             min_value=1, max_value=10000,
                                             localize=True,
                                             error_messages={"required": ERROR_MESSAGES["COMPANY_NUMBER_EMPLOYEES"]})

    gross_turnover = forms.DecimalField(widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                      "maxlength": "10",
                                                                      "class": "form-control-inline"}),
                                        max_digits=10,
                                        decimal_places=2,
                                        localize=True,
                                        help_text=_("For example, 150000"),
                                        error_messages={"required": ERROR_MESSAGES["COMPANY_GROSS_TURNOVER"]})

    net_turnover = forms.DecimalField(widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                    "maxlength": "10",
                                                                    "class": "form-control-inline"}),
                                      help_text=_("For example, 110000"),
                                      max_digits=10,
                                      decimal_places=2,
                                      localize=True,
                                      error_messages={"required": ERROR_MESSAGES["COMPANY_NET_TURNOVER"]})

    def __init__(self, *args, **kwargs):
        super(CompanyFinancesForm, self).__init__(*args, **kwargs)
        try:
            data = args[0]
        except IndexError:
            data = {}

        if data:
            for field_name, dependency in self.depdencies.items():
                dependency_field = dependency["required"].get("field", None)
                dependency_value = dependency["required"].get("value", None)
                if dependency_field:
                    if dependency_value:
                        if data.get(dependency_field, None) != dependency_value:
                            self.fields[field_name].required = True
                        else:
                            self.fields[field_name].required = False
                    else:
                        if data.get(dependency_field, None) is not None:
                            self.fields[field_name].required = True
                        else:
                            self.fields[field_name].required = False

        if "trading_period" in data:
            if not "nojs_first_question" in data:
              self.fields["number_of_employees"].required = True
              self.fields["gross_turnover"].required = True
              self.fields["net_turnover"].required = True

            if data["trading_period"] == "False":
                self.fields["gross_turnover"].error_messages = {"required": ERROR_MESSAGES["COMPANY_GROSS_TURNOVER_PROJECTED"]}
                self.fields["net_turnover"].error_messages = {"required": ERROR_MESSAGES["COMPANY_NET_TURNOVER_PROJECTED"]}


class ConfirmationForm(BasePleaStepForm):
    understand = forms.BooleanField(required=True,
                                    error_messages={"required": ERROR_MESSAGES["UNDERSTAND_REQUIRED"]})


class PleaForm(BasePleaStepForm):
    PLEA_CHOICES = (
        ('guilty', _('Guilty')),
        ('not_guilty', _('Not guilty')),
    )

    def __init__(self, *args, **kwargs):

        super(PleaForm, self).__init__(*args, **kwargs)

        prefix = kwargs.get("prefix", "")

        if "data" in kwargs:

            plea = kwargs["data"].get("{}-guilty".format(prefix), None)

            if plea == "not_guilty":
                self.fields["not_guilty_extra"].required = True
            else:
                self.fields["not_guilty_extra"].required = False

    guilty = forms.ChoiceField(choices=PLEA_CHOICES, widget=RadioSelect(), required=True,
                               error_messages={"required": ERROR_MESSAGES["PLEA_REQUIRED"]})
    
    guilty_extra = forms.CharField(label=_("Mitigation"),
                                   widget=Textarea(attrs={"class": "form-control", "rows": "4"}),
                                   help_text=_("What would you like the court to consider?"),
                                   required=False,
                                   max_length=5000)

    not_guilty_extra = forms.CharField(label=_("Not guilty because?"),
                                       widget=Textarea(attrs={"class": "form-control", "rows": "4"}),
                                       help_text=_("Tell us why you believe you are not guilty"),
                                       required=False,
                                       max_length=5000)


class CourtFinderForm(forms.Form):
    urn = URNField(label=_("Unique reference number (URN)"),
                   required=True,
                   help_text=_("On page 1 of the pack, in the top right corner.<br>For example, 12/AB/34567/00"),
                   error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"]})

    def clean_urn(self):
        urn = self.cleaned_data["urn"]

        try:
            is_urn_valid(urn)
        except forms.ValidationError:
            raise forms.ValidationError("You've entered incorrect details")
        return urn
