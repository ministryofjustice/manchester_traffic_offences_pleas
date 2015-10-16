from __future__ import unicode_literals

from collections import OrderedDict

from django import forms
from django.forms.widgets import Textarea, RadioSelect
from django.utils.translation import ugettext_lazy as _

from apps.forms.fields import DSRadioFieldRenderer, DateWidget
from apps.forms.forms import (YESNO_CHOICES,
                              to_bool,
                              BaseStageForm,
                              SplitStageForm)

from .fields import ERROR_MESSAGES
from .validators import (is_date_in_past,
                         is_date_in_future,
                         is_date_in_last_28_days,
                         is_date_in_next_6_months,
                         is_urn_not_used,
                         is_urn_valid)


def reorder_fields(fields, order):
    for key, v in fields.items():
        if key not in order:
            del fields[key]

    return OrderedDict(sorted(fields.items(), key=lambda k: order.index(k[0])))


class NoticeTypeForm(BaseStageForm):
    sjp = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                 required=True,
                                 coerce=to_bool,
                                 choices=YESNO_CHOICES["Ydy/Nac ydy"],
                                 label=_("Is the title at the very top, next to the police logo, 'Single Justice Procedure Notice'?"),
                                 help_text=_("If your paperwork does not have Single Justice Procedure Notice written in the place shown, select no to continue."),
                                 error_messages={"required": ERROR_MESSAGES["NOTICE_TYPE_REQUIRED"]})


class BaseCaseForm(BaseStageForm):
    PLEA_MADE_BY_CHOICES = (
        ("Defendant", _("The person named in the notice")),
        ("Company representative", _("Pleading on behalf of a company")))

    urn = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                          label=_("Unique reference number (URN)"),
                          required=True,
                          validators=[is_urn_valid, is_urn_not_used],
                          help_text=_("On page 1 of the notice, usually at the top."),
                          error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"],
                                          "is_urn_valid": ERROR_MESSAGES["URN_INVALID"],
                                          "is_urn_not_used": ERROR_MESSAGES['URN_ALREADY_USED']})

    number_of_charges = forms.IntegerField(label=_("Number of charges"),
                                           widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                         "maxlength": "2",
                                                                         "class": "form-control-inline",
                                                                         "size": "2"}),
                                           help_text=_("On the charge sheet, in numbered boxes."),
                                           min_value=1, max_value=10,
                                           error_messages={"required": ERROR_MESSAGES["NUMBER_OF_CHARGES_REQUIRED"]})

    plea_made_by = forms.TypedChoiceField(required=True, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                          choices=PLEA_MADE_BY_CHOICES,
                                          label=_("Are you? (plea made by)"),
                                          help_text=_("Choose one of the following options:"),
                                          error_messages={"required": ERROR_MESSAGES["PLEA_MADE_BY_REQUIRED"]})

class CaseForm(BaseCaseForm):
    date_of_hearing = forms.DateField(widget=DateWidget,
                                      validators=[is_date_in_future, is_date_in_next_6_months],
                                      required=True,
                                      label=_("Court hearing date"),
                                      help_text=_("On page 1 of the notice, near the top. <br>For example, 30/07/2014"),
                                      error_messages={"required": ERROR_MESSAGES["HEARING_DATE_REQUIRED"],
                                                      "invalid": ERROR_MESSAGES["HEARING_DATE_INVALID"],
                                                      "is_date_in_future": ERROR_MESSAGES["HEARING_DATE_PASSED"],
                                                      "is_date_within_range": ERROR_MESSAGES["HEARING_DATE_INCORRECT"]})

    def __init__(self, *args, **kwargs):
        super(CaseForm, self).__init__(*args, **kwargs)
        fields_order = ["urn", "date_of_hearing", "number_of_charges", "plea_made_by"]
        self.fields = reorder_fields(self.fields, fields_order)


class SJPCaseForm(BaseCaseForm):
    posting_date = forms.DateField(widget=DateWidget,
                                   validators=[is_date_in_past, is_date_in_last_28_days],
                                   required=True,
                                   label=_("Posting date"),
                                   help_text=_("On page 1 of the notice, near the top. <br>For example, 30/07/2014"),
                                   error_messages={"required": ERROR_MESSAGES["POSTING_DATE_REQUIRED"],
                                                   "invalid": ERROR_MESSAGES["POSTING_DATE_INVALID"],
                                                   "is_date_in_past": ERROR_MESSAGES["POSTING_DATE_IN_FUTURE"]})

    def __init__(self, *args, **kwargs):
        super(SJPCaseForm, self).__init__(*args, **kwargs)
        fields_order = ["urn", "posting_date", "number_of_charges", "plea_made_by"]
        self.fields = reorder_fields(self.fields, fields_order)


class YourDetailsForm(BaseStageForm):
    dependencies = {
        "updated_address": {
            "field": "correct_address",
            "value": "False"
        },
        "ni_number": {
            "field": "have_ni_number",
            "value": "True"
        },
        "driving_licence_number": {
            "field": "have_driving_licence_number",
            "value": "True"
        }
    }

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
                                             choices=YESNO_CHOICES["Ydy/Nac ydy"],
                                             label=_("Is your address correct on page 1 of the notice we sent to you?"),
                                             error_messages={"required": ERROR_MESSAGES["CORRECT_ADDRESS_REQUIRED"]})

    updated_address = forms.CharField(widget=forms.Textarea(attrs={"rows": "4", "class": "form-control"}),
                                      required=False,
                                      label="",
                                      help_text=_("If no, tell us your correct address here:"),
                                      error_messages={"required": ERROR_MESSAGES["UPDATED_ADDRESS_REQUIRED"]})

    contact_number = forms.CharField(widget=forms.TextInput(attrs={"type": "tel", "class": "form-control"}),
                                     required=True,
                                     max_length=30,
                                     label=_("Contact number"),
                                     help_text=_("Landline or mobile number."),
                                     error_messages={"required": ERROR_MESSAGES["CONTACT_NUMBER_REQUIRED"],
                                                     "invalid": ERROR_MESSAGES["CONTACT_NUMBER_INVALID"]})

    date_of_birth = forms.DateField(widget=DateWidget,
                                    required=True,
                                    validators=[is_date_in_past],
                                    label=_("Date of birth"),
                                    error_messages={"required": ERROR_MESSAGES["DATE_OF_BIRTH_REQUIRED"],
                                                    "invalid": ERROR_MESSAGES["DATE_OF_BIRTH_INVALID"],
                                                    "is_date_in_past": ERROR_MESSAGES["DATE_OF_BIRTH_IN_FUTURE"]})

    have_ni_number = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            required=True,
                                            coerce=to_bool,
                                            choices=YESNO_CHOICES["Oes/Nac oes"],
                                            label=_("Do you have a National Insurance number?"),
                                            error_messages={"required": ERROR_MESSAGES["HAVE_NI_NUMBER_REQUIRED"]})

    ni_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                required=True,
                                label="",
                                help_text=_("If yes, enter it here. It can be found on your National Insurance card, benefit letter, payslip or P60 - for example, 'QQ 12 34 56 C'"),
                                error_messages={"required": ERROR_MESSAGES["NI_NUMBER_REQUIRED"]})

    have_driving_licence_number = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                         required=True,
                                                         coerce=to_bool,
                                                         choices=YESNO_CHOICES["Oes/Nac oes"],
                                                         label=_("Do you have a UK driving licence?"),
                                                         help_text=_("Entering your UK driving licence number means you don't have to send your licence to the court."),
                                                         error_messages={"required": ERROR_MESSAGES["HAVE_DRIVING_LICENCE_NUMBER_REQUIRED"]})

    driving_licence_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                             required=True,
                                             label="",
                                             help_text=_("If yes, enter it here. It's on your driving licence photocard and starts with letters from your last name."),
                                             error_messages={"required": ERROR_MESSAGES["DRIVING_LICENCE_NUMBER_REQUIRED"]})


class CompanyDetailsForm(BaseStageForm):
    dependencies = {
        "updated_address": {
            "field": "correct_address",
            "value": "False"
        }
    }

    COMPANY_POSITION_CHOICES = (
        ("Director", _("director")),
        ("Company secretary", _("company secretary")),
        ("Company solicitor", _("company solicitor")))

    company_name = forms.CharField(label=_("Company name"),
                                   widget=forms.TextInput(attrs={"class": "form-control"}),
                                   max_length=100,
                                   required=True,
                                   help_text=_("As written on page 1 of the notice we sent you."),
                                   error_messages={"required": ERROR_MESSAGES["COMPANY_NAME_REQUIRED"]})

    correct_address = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                             coerce=to_bool,
                                             choices=YESNO_CHOICES["Ydy/Nac ydy"],
                                             required=True,
                                             label=_("Is the company's address correct on page 1 of the notice we sent to you?"),
                                             error_messages={"required": ERROR_MESSAGES["COMPANY_CORRECT_ADDRESS_REQUIRED"]})

    updated_address = forms.CharField(widget=forms.Textarea(attrs={"rows": "4", "class": "form-control"}),
                                      label="",
                                      required=False,
                                      help_text=_("If no, tell us the correct company address here:"),
                                      error_messages={"required": ERROR_MESSAGES["COMPANY_UPDATED_ADDRESS_REQUIRED"]})

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
                                            widget=RadioSelect(renderer=DSRadioFieldRenderer),
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


class YourMoneyForm(SplitStageForm):

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

    dependencies = {
        "employed_take_home_pay_period": {"field": "you_are", "value": "Employed"},
        "employed_take_home_pay_amount": {"field": "you_are", "value": "Employed"},
        "employed_hardship": {"field": "you_are", "value": "Employed"},

        "self_employed_pay_period": {"field": "you_are", "value": "Self-employed"},
        "self_employed_pay_other": {"field": "self_employed_pay_period", "value": "Self-employed other"},

        "self_employed_pay_amount": {"field": "you_are", "value": "Self-employed"},
        "self_employed_hardship": {"field": "you_are", "value": "Self-employed"},

        "benefits_details": {"field": "you_are", "value": "Receiving benefits"},
        "benefits_dependents": {"field": "you_are", "value": "Receiving benefits"},
        "benefits_period": {"field": "you_are", "value": "Receiving benefits"},
        "benefits_pay_other": {"field": "benefits_period", "value": "Benefits other"},
        "benefits_amount": {"field": "you_are", "value": "Receiving benefits"},
        "receiving_benefits_hardship": {"field": "you_are", "value": "Receiving benefits"},

        "other_details": {"field": "you_are", "value": "Other"},
        "other_pay_amount": {"field": "you_are", "value": "Other"},
        "other_hardship": {"field": "you_are", "value": "Other"}
    }

    split_form_options = {
        "trigger": "you_are"
    }

    you_are = forms.ChoiceField(label=_("Are you? (employment status)"), choices=YOU_ARE_CHOICES,
                                widget=forms.RadioSelect(renderer=DSRadioFieldRenderer),
                                error_messages={"required": ERROR_MESSAGES["YOU_ARE_REQUIRED"]})
    # Employed
    employed_take_home_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                      choices=PERIOD_CHOICES,
                                                      label=_("How often do you get paid?"),
                                                      error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                      "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})

    employed_take_home_pay_amount = forms.DecimalField(label=_("What's your take home pay (after tax)?"),
                                                       localize=True,
                                                       widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                                     "data-template-trigger": "employed_take_home_pay_period",
                                                                                     "data-template": _("What's your {value} take home pay (after tax)?"),
                                                                                     "data-template-delegate": "[for=id_employed_take_home_pay_amount] .label-text",
                                                                                     "class": "form-control-inline"}),
                                                       error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                                       "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    employed_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                               help_text=_("For example, you would become homeless."),
                                               widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                               choices=YESNO_CHOICES["Byddai/Na fyddai"],
                                               coerce=to_bool,
                                               error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})

    # Self-employed
    self_employed_pay_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                 choices=SE_PERIOD_CHOICES,
                                                 label=_("How often do you get paid?"),
                                                 error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                                 "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})

    self_employed_pay_amount = forms.DecimalField(label=_("What's your average take home pay?"),
                                                  localize=True,
                                                  widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                                "data-template-trigger": "self_employed_pay_period",
                                                                                "data-template": _("What's your average {value} take home pay?"),
                                                                                "data-template-defaults-for": _("Other"),
                                                                                "data-template-delegate": "[for=id_self_employed_pay_amount] .label-text",
                                                                                "class": "form-control-inline"}),
                                                  error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                                  "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    self_employed_pay_other = forms.CharField(label="",
                                              max_length=500,
                                              widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                              help_text=_("If you selected 'other', tell us how often you get paid."))

    self_employed_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                                    help_text=_("For example, you would become homeless."),
                                                    widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                    choices=YESNO_CHOICES["Byddai/Na fyddai"],
                                                    coerce=to_bool,
                                                    error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})

    # On benefits
    benefits_details = forms.CharField(label=_("Which benefits do you receive?"),
                                       help_text=_("For example, Income Support or Disability Living Allowance."),
                                       max_length=500,
                                       widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                       error_messages={"required": ERROR_MESSAGES["BENEFITS_DETAILS_REQUIRED"]})

    benefits_dependents = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YESNO_CHOICES["Ydy/Nac ydy"],
                                            coerce=to_bool,
                                            label=_("Does this include payment for dependants?"),
                                            error_messages={"required": ERROR_MESSAGES["BENEFITS_DEPENDANTS_REQUIRED"]})

    benefits_period = forms.ChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                        choices=BEN_PERIOD_CHOICES,
                                        label=_("How often are your benefits paid?"),
                                        error_messages={"required": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"],
                                                        "incomplete": ERROR_MESSAGES["PAY_PERIOD_REQUIRED"]})

    benefits_pay_other = forms.CharField(label="",
                                         max_length=500,
                                         widget=forms.Textarea(attrs={"rows": "2", "class": "form-control"}),
                                         help_text=_("If you selected 'other', tell us how often you get paid."))

    benefits_amount = forms.DecimalField(label=_("What's your average take home pay?"),
                                         localize=True,
                                         widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                       "data-template-trigger": "benefits_period",
                                                                       "data-template": _("What's your average {value} take home pay?"),
                                                                       "data-template-defaults-for": _("Other"),
                                                                       "data-template-delegate": "[for=id_benefits_amount] .label-text",
                                                                       "class": "form-control-inline"}),
                                         error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                         "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    receiving_benefits_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                                         help_text=_("For example, you would become homeless."),
                                                         widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                         choices=YESNO_CHOICES["Byddai/Na fyddai"],
                                                         coerce=to_bool,
                                                         error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})

    # Other
    other_details = forms.CharField(max_length=500, label=_("Provide details"),
                                    help_text=_("For example, student or retired."),
                                    widget=forms.TextInput(attrs={"class": "form-control"}),
                                    error_messages={"required": ERROR_MESSAGES["OTHER_INFO_REQUIRED"]})

    other_pay_amount = forms.DecimalField(label=_("What is your monthly disposable income?"),
                                          localize=True,
                                          widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                        "class": "form-control-inline"}),
                                          error_messages={"required": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"],
                                                          "incomplete": ERROR_MESSAGES["PAY_AMOUNT_REQUIRED"]})

    other_hardship = forms.TypedChoiceField(label=_("Would paying a fine cause you serious financial problems?"),
                                            help_text=_("For example, you would become homeless."),
                                            widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YESNO_CHOICES["Byddai/Na fyddai"],
                                            coerce=to_bool,
                                            error_messages={"required": ERROR_MESSAGES["HARDSHIP_REQUIRED"]})


class HardshipForm(BaseStageForm):
    hardship_details = forms.CharField(
        label=_("How would paying a fine cause you serious financial problems?"),
        help_text=_("What the court should consider when deciding how much your fine should be:"),
        widget=forms.Textarea(attrs={"cols": 45, "rows": 5, "class": "form-control"}),
        required=True,
        error_messages={"required": ERROR_MESSAGES["HARDSHIP_DETAILS_REQUIRED"]})


class HouseholdExpensesForm(BaseStageForm):
    household_accommodation = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Accommodation"),
        help_text=_("Rent, mortgage or lodgings"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["HOUSEHOLD_ACCOMMODATION_REQUIRED"],
                        "invalid": ERROR_MESSAGES["HOUSEHOLD_ACCOMMODATION_INVALID"],
                        "min_value": ERROR_MESSAGES["HOUSEHOLD_ACCOMMODATION_MIN"]})

    household_utility_bills = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Utility bills"),
        help_text=_("Gas, water, electricity etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["HOUSEHOLD_UTILITY_BILLS_REQUIRED"],
                        "invalid": ERROR_MESSAGES["HOUSEHOLD_UTILITY_BILLS_INVALID"],
                        "min_value": ERROR_MESSAGES["HOUSEHOLD_UTILITY_BILLS_MIN"]})

    household_insurance = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Insurance"),
        help_text=_("Home, life insurance etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["HOUSEHOLD_INSURANCE_REQUIRED"],
                        "invalid": ERROR_MESSAGES["HOUSEHOLD_INSURANCE_INVALID"],
                        "min_value": ERROR_MESSAGES["HOUSEHOLD_INSURANCE_MIN"]})

    household_council_tax = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Council tax"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["HOUSEHOLD_COUNCIL_TAX_REQUIRED"],
                        "invalid": ERROR_MESSAGES["HOUSEHOLD_COUNCIL_TAX_INVALID"],
                        "min_value": ERROR_MESSAGES["HOUSEHOLD_COUNCIL_TAX_MIN"]})

    other_bill_payers = forms.TypedChoiceField(
        widget=RadioSelect(renderer=DSRadioFieldRenderer),
        label=_("Does anyone else contribute to these bills?"),
        choices=YESNO_CHOICES["Oes/Nac oes"],
        coerce=to_bool,
        error_messages={"required": ERROR_MESSAGES["OTHER_BILL_PAYERS_REQUIRED"]})


class OtherExpensesForm(BaseStageForm):
    other_tv_subscription = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Television subscription"),
        help_text=_("TV licence, satellite etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["OTHER_TV_SUBSCRIPTION_REQUIRED"],
                        "invalid": ERROR_MESSAGES["OTHER_TV_SUBSCRIPTION_INVALID"],
                        "min_value": ERROR_MESSAGES["OTHER_TV_SUBSCRIPTION_MIN"]})

    other_travel_expenses = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Travel expenses"),
        help_text=_("Fuel, car, public transport etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["OTHER_TRAVEL_EXPENSES_REQUIRED"],
                        "invalid": ERROR_MESSAGES["OTHER_TRAVEL_EXPENSES_INVALID"],
                        "min_value": ERROR_MESSAGES["OTHER_TRAVEL_EXPENSES_MIN"]})

    other_telephone = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Telephone"),
        help_text=_("Landline and/or mobile"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["OTHER_TELEPHONE_REQUIRED"],
                        "invalid": ERROR_MESSAGES["OTHER_TELEPHONE_INVALID"],
                        "min_value": ERROR_MESSAGES["OTHER_TELEPHONE_MIN"]})

    other_loan_repayments = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Loan repayments"),
        help_text=_("Credit card, bank etc"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["OTHER_LOAN_REPAYMENTS_REQUIRED"],
                        "invalid": ERROR_MESSAGES["OTHER_LOAN_REPAYMENTS_INVALID"],
                        "min_value": ERROR_MESSAGES["OTHER_LOAN_REPAYMENTS_MIN"]})

    other_court_payments = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("County court orders"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["OTHER_COURT_PAYMENTS_REQUIRED"],
                        "invalid": ERROR_MESSAGES["OTHER_COURT_PAYMENTS_INVALID"],
                        "min_value": ERROR_MESSAGES["OTHER_COURT_PAYMENTS_MIN"]})

    other_child_maintenance = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        localize=True,
        required=False,
        label=_("Child maintenance"),
        widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                      "class": "form-control-inline"}),
        error_messages={"required": ERROR_MESSAGES["OTHER_CHILD_MAINTENANCE_REQUIRED"],
                        "invalid": ERROR_MESSAGES["OTHER_CHILD_MAINTENANCE_INVALID"],
                        "min_value": ERROR_MESSAGES["OTHER_CHILD_MAINTENANCE_MIN"]})


class CompanyFinancesForm(SplitStageForm):
    dependencies = {
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

    split_form_options = {
        "trigger": "trading_period",
        "nojs_only": True
    }

    trading_period = forms.TypedChoiceField(required=True, widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            choices=YESNO_CHOICES["Ydy/Nac ydy"],
                                            coerce=to_bool,
                                            label=_("Has the company been trading for more than 12 months?"),
                                            error_messages={"required": ERROR_MESSAGES["COMPANY_TRADING_PERIOD"]})

    number_of_employees = forms.IntegerField(label=_("Number of employees"),
                                             widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                           "maxlength": "5",
                                                                           "class": "form-control-inline"}),
                                             min_value=1,
                                             max_value=10000,
                                             localize=True,
                                             error_messages={"required": ERROR_MESSAGES["COMPANY_NUMBER_EMPLOYEES"]})

    gross_turnover = forms.DecimalField(widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                      "maxlength": "10",
                                                                      "class": "form-control-inline"}),
                                        max_digits=10,
                                        decimal_places=2,
                                        localize=True,
                                        label=_("Gross turnover"),
                                        help_text=_("For example, 150000"),
                                        error_messages={"required": ERROR_MESSAGES["COMPANY_GROSS_TURNOVER"]})

    net_turnover = forms.DecimalField(widget=forms.TextInput(attrs={"pattern": "[0-9]*",
                                                                    "maxlength": "10",
                                                                    "class": "form-control-inline"}),
                                      label=_("Net turnover"),
                                      help_text=_("For example, 110000"),
                                      max_digits=10,
                                      decimal_places=2,
                                      localize=True,
                                      error_messages={"required": ERROR_MESSAGES["COMPANY_NET_TURNOVER"]})

    def __init__(self, *args, **kwargs):
        super(CompanyFinancesForm, self).__init__(*args, **kwargs)

        if self.data.get("trading_period") == "False":
            self.fields["gross_turnover"].error_messages.update({"required": ERROR_MESSAGES["COMPANY_GROSS_TURNOVER_PROJECTED"]})
            self.fields["net_turnover"].error_messages.update({"required": ERROR_MESSAGES["COMPANY_NET_TURNOVER_PROJECTED"]})
        else:
            self.fields["gross_turnover"].error_messages.update({"required": ERROR_MESSAGES["COMPANY_GROSS_TURNOVER"]})
            self.fields["net_turnover"].error_messages.update({"required": ERROR_MESSAGES["COMPANY_NET_TURNOVER"]})


class ConfirmationForm(BaseStageForm):
    dependencies = {
        "email": {
            "field": "receive_email_updates",
            "value": "True"
        }
    }

    receive_email_updates = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                   required=True,
                                                   coerce=to_bool,
                                                   choices=YESNO_CHOICES["Ydw/Nac ydw"],
                                                   label=_("Do you want to receive email updates about your case?"),
                                                   help_text=_("We'll use this for all future correspondence as well as contacting you by post."),
                                                   error_messages={"required": ERROR_MESSAGES["RECEIVE_EMAIL_UPDATES_REQUIRED"]})

    email = forms.EmailField(widget=forms.TextInput(attrs={"type": "email", "class": "form-control"}),
                                          required=False,
                                          label="",
                                          help_text=_("If yes, enter your email address here:"),
                                          error_messages={"required": ERROR_MESSAGES["UPDATES_EMAIL_REQUIRED"],
                                                          "invalid": ERROR_MESSAGES["EMAIL_ADDRESS_INVALID"]})

    understand = forms.BooleanField(required=True,
                                    error_messages={"required": ERROR_MESSAGES["UNDERSTAND_REQUIRED"]})


class BasePleaForm(SplitStageForm):
    PLEA_CHOICES = (
        ('guilty', _('Guilty')),
        ('not_guilty', _('Not guilty')),
    )

    split_form_options = {
        "trigger": "guilty",
        "nojs_only": True
    }

    guilty = forms.ChoiceField(choices=PLEA_CHOICES, widget=RadioSelect(), required=True,
                               error_messages={"required": ERROR_MESSAGES["PLEA_REQUIRED"]})

    guilty_extra = forms.CharField(label=_("Mitigation"),
                                   widget=Textarea(attrs={"class": "form-control", "rows": "4"}),
                                   help_text=_("Is there something you would like the court to consider?"),
                                   required=False,
                                   max_length=5000)

    not_guilty_extra = forms.CharField(label=_("Not guilty because?"),
                                       widget=Textarea(attrs={"class": "form-control", "rows": "4"}),
                                       help_text=_("Why do you believe you are not guilty?"),
                                       max_length=5000,
                                       error_messages={"required": ERROR_MESSAGES["NOT_GUILTY_REQUIRED"]})

    interpreter_needed = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                required=True,
                                                choices=YESNO_CHOICES["Oes/Nac oes"],
                                                coerce=to_bool,
                                                label=_("Do you need an interpreter in court?"),
                                                error_messages={"required": ERROR_MESSAGES["INTERPRETER_NEEDED_REQUIRED"]})

    interpreter_language = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                           max_length=100,
                                           required=True,
                                           label="",
                                           help_text=_("If yes, tell us which language (include sign language):"),
                                           error_messages={"required": ERROR_MESSAGES["INTERPRETER_LANGUAGE_REQUIRED"]})

    disagree_with_evidence = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                    required=True,
                                                    choices=YESNO_CHOICES["Oes/Nac oes"],
                                                    coerce=to_bool,
                                                    label=_("Do you disagree with any evidence from a witness statement in the notice we sent to you?"),
                                                    error_messages={"required": ERROR_MESSAGES["DISAGREE_WITH_EVIDENCE_REQUIRED"]})

    disagree_with_evidence_details = forms.CharField(label="",
                                                     widget=Textarea(attrs={"class": "form-control", "rows": "3"}),
                                                     help_text=_("If yes, tell us the name of the witness (on the top left of the statement) and what you disagree with:"),
                                                     max_length=5000,
                                                     error_messages={"required": ERROR_MESSAGES["DISAGREE_WITH_EVIDENCE_DETAILS_REQUIRED"]})

    witness_needed = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                            required=True,
                                            choices=YESNO_CHOICES["Oes/Nac oes"],
                                            coerce=to_bool,
                                            label=_("Do you want to call a defence witness?"),
                                            help_text=_("Someone who can give evidence in court supporting your case."),
                                            error_messages={"required": ERROR_MESSAGES["WITNESS_NEEDED_REQUIRED"]})

    witness_details = forms.CharField(label="",
                                      widget=Textarea(attrs={"class": "form-control", "rows": "3"}),
                                      help_text=_("If yes, tell us the name, address and date of birth of any witnesses you want to call  to support your case:"),
                                      max_length=5000,
                                      error_messages={"required": ERROR_MESSAGES["WITNESS_DETAILS_REQUIRED"]})

    witness_interpreter_needed = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                        required=True,
                                                        choices=YESNO_CHOICES["Oes/Nac oes"],
                                                        coerce=to_bool,
                                                        label=_("Does your witness need an interpreter in court?"),
                                                        error_messages={"required": ERROR_MESSAGES["WITNESS_INTERPRETER_NEEDED_REQUIRED"]})

    witness_interpreter_language = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                                   max_length=100,
                                                   required=True,
                                                   label="",
                                                   help_text=_("If yes, tell us which language (include sign language):"),
                                                   error_messages={"required": ERROR_MESSAGES["WITNESS_INTERPRETER_LANGUAGE_REQUIRED"]})

class PleaForm(BasePleaForm):
    dependencies = OrderedDict([
        ("not_guilty_extra", {"field": "guilty", "value": "not_guilty"}),
        ("interpreter_needed", {"field": "guilty", "value": "not_guilty"}),
        ("interpreter_language", {"field": "interpreter_needed", "value": "True"}),
        ("disagree_with_evidence", {"field": "guilty", "value": "not_guilty"}),
        ("disagree_with_evidence_details", {"field": "disagree_with_evidence", "value": "True"}),
        ("witness_needed", {"field": "guilty", "value": "not_guilty"}),
        ("witness_details", {"field": "witness_needed", "value": "True"}),
        ("witness_interpreter_needed", {"field": "witness_needed", "value": "True"}),
        ("witness_interpreter_language", {"field": "witness_interpreter_needed", "value": "True"})
    ])


class SJPPleaForm(BasePleaForm):
    dependencies = OrderedDict([
        ("come_to_court", {"field": "guilty", "value": "guilty"}),
        ("sjp_interpreter_needed", {"field": "come_to_court", "value": "True"}),
        ("sjp_interpreter_language", {"field": "sjp_interpreter_needed", "value": "True"}),
        ("not_guilty_extra", {"field": "guilty", "value": "not_guilty"}),
        ("interpreter_needed", {"field": "guilty", "value": "not_guilty"}),
        ("interpreter_language", {"field": "interpreter_needed", "value": "True"}),
        ("disagree_with_evidence", {"field": "guilty", "value": "not_guilty"}),
        ("disagree_with_evidence_details", {"field": "disagree_with_evidence", "value": "True"}),
        ("witness_needed", {"field": "guilty", "value": "not_guilty"}),
        ("witness_details", {"field": "witness_needed", "value": "True"}),
        ("witness_interpreter_needed", {"field": "witness_needed", "value": "True"}),
        ("witness_interpreter_language", {"field": "witness_interpreter_needed", "value": "True"})
    ])

    come_to_court = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                           required=True,
                                           choices=YESNO_CHOICES["Oes/Nac oes"],
                                           coerce=to_bool,
                                           label=_("Do you want to come to court to plead guilty?"),
                                           error_messages={"required": ERROR_MESSAGES["COME_TO_COURT_REQUIRED"]})

    sjp_interpreter_needed = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                                    required=True,
                                                    choices=YESNO_CHOICES["Oes/Nac oes"],
                                                    coerce=to_bool,
                                                    label=_("Do you need an interpreter in court?"),
                                                    error_messages={"required": ERROR_MESSAGES["INTERPRETER_NEEDED_REQUIRED"]})

    sjp_interpreter_language = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                                               max_length=100,
                                               required=True,
                                               label="",
                                               help_text=_("If yes, tell us which language (include sign language):"),
                                               error_messages={"required": ERROR_MESSAGES["INTERPRETER_LANGUAGE_REQUIRED"]})

    def __init__(self, *args, **kwargs):
        super(SJPPleaForm, self).__init__(*args, **kwargs)
        fields_order = ["split_form",
                        "guilty",
                        "come_to_court",
                        "sjp_interpreter_needed",
                        "sjp_interpreter_language",
                        "guilty_extra",
                        "not_guilty_extra",
                        "interpreter_needed",
                        "interpreter_language",
                        "disagree_with_evidence",
                        "disagree_with_evidence_details",
                        "witness_needed",
                        "witness_details",
                        "witness_interpreter_needed",
                        "witness_interpreter_language"]
        self.fields = reorder_fields(self.fields, fields_order)


class CourtFinderForm(forms.Form):
    urn = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}),
                          label=_("Unique reference number (URN)"),
                          required=True,
                          validators=[is_urn_valid],
                          help_text=_("On page 1, usually at the top."),
                          error_messages={"required": ERROR_MESSAGES["URN_REQUIRED"],
                                          "is_urn_valid": ERROR_MESSAGES["URN_INCORRECT"]})
