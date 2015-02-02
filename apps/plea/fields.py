from dateutil.parser import parse
import datetime
import re
import six

from django.conf import settings
from django.core import exceptions
from django import forms
from django.forms.widgets import (MultiWidget, RadioSelect,
                                  TextInput, RadioFieldRenderer)
from django.forms.extras.widgets import Widget
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _

from .models import Case


ERROR_MESSAGES = {
    "URN_REQUIRED": "Enter your unique reference number (URN)",
    "URN_INVALID": "The unique reference number (URN) isn't valid. Enter the number exactly as it appears on page 1 of the pack",
    "URN_ALREADY_USED": "Enter the correct URN",
    "HEARING_DATE_REQUIRED": "Provide a court hearing date",
    "HEARING_DATE_INVALID": "The court hearing date isn't a valid format",
    "HEARING_DATE_PASSED": "The court hearing date must be after today",
    "NUMBER_OF_CHARGES_REQUIRED": "Select the number of charges against you",
    "FULL_NAME_REQUIRED": "Please enter your full name",
    "EMAIL_ADDRESS_REQUIRED": "You must provide an email address",
    "EMAIL_ADDRESS_INVALID": "Email address isn't a valid format",
    "CONTACT_NUMBER_REQUIRED": "You must provide a contact number",
    "CONTACT_NUMBER_INVALID": "The contact number isn't a valid format",
    "PLEA_REQUIRED": "Your plea must be selected",
    "YOU_ARE_REQUIRED": "You must let us know if you're employed, receiving benefits or other",
    "EMPLOYED_JOB_REQUIRED": "Please tell us what your job is",
    "EMPLOYERS_NAME_REQUIRED": "Please enter your employer's full name",
    "EMPLOYERS_ADDRESS_REQUIRED": "You must provide your employer's full address",
    "EMPLOYERS_PHONE_REQUIRED": "Please enter your employer's phone number",
    "PAY_PERIOD_REQUIRED": "Please enter how often you get paid",
    "PAY_AMOUNT_REQUIRED": "Please enter your take home pay",
    "YOUR_JOB_REQUIRED": "Please tell us what your job is",
    "SELF_EMPLOYED_PAY_REQUIRED": "Please enter your take home pay and how often you're paid",
    "BENEFITS_REQUIRED": "Please enter total benefits and how often you receive them",
    "UNDERSTAND_REQUIRED": "You must confirm that you have read & understood the charge against you before you can submit your plea",
    "OTHER_INFO_REQUIRED": "Please let us know how you earn your money",
    "RECEIVE_EMAIL": "You must choose whether you want to receive court correspondence through email",
    "HARDSHIP_DETAILS_REQUIRED": "You must tell us why paying a fine will cause you serious financial problems",
    "OTHER_BILL_PAYERS_REQUIRED": "You must tell us if anyone else contributes to your household bills.",
    "HOUSEHOLD_ACCOMMODATION_REQUIRED": "Accommodation is a required field",
    "HOUSEHOLD_ACCOMMODATION_INVALID": "Accommodation must be a number",
    "HOUSEHOLD_ACCOMMODATION_MIN": "Accommodation must be a number greater than, or equal to, 0",
    "HOUSEHOLD_UTILITY_BILLS_REQUIRED": "Utility bills is a required field",
    "HOUSEHOLD_UTILITY_BILLS_INVALID": "Utility bills must be a number",
    "HOUSEHOLD_UTILITY_BILLS_MIN": "Utility bills must be a number greater than, or equal to, 0",
    "HOUSEHOLD_INSURANCE_REQUIRED": "Insurance is a required field",
    "HOUSEHOLD_INSURANCE_INVALID": "Insurance must be a number",
    "HOUSEHOLD_INSURANCE_MIN": "Insurance must be a number greater than, or equal to, 0",
    "HOUSEHOLD_COUNCIL_TAX_REQUIRED": "Council tax is a required field",
    "HOUSEHOLD_COUNCIL_TAX_INVALID": "Council tax must be a number",
    "HOUSEHOLD_COUNCIL_TAX_MIN": "Council tax must be a number greater than, or equal to, 0",
    "OTHER_TV_SUBSCRIPTION_REQUIRED": "TV subscription is a required field",
    "OTHER_TV_SUBSCRIPTION_INVALID": "TV subscription must be a number",
    "OTHER_TV_SUBSCRIPTION_MIN": "TV subscription must be a number greater than, or equal to, 0",
    "OTHER_TRAVEL_EXPENSES_REQUIRED": "Travel expenses is a required field",
    "OTHER_TRAVEL_EXPENSES_INVALID": "Travel expenses must be a number",
    "OTHER_TRAVEL_EXPENSES_MIN": "Travel expenses must be a number greater than, or equal to, 0",
    "OTHER_TELEPHONE_REQUIRED": "Telephone is a required field",
    "OTHER_TELEPHONE_INVALID": "Telephone must be a number",
    "OTHER_TELEPHONE_MIN": "Telephone must be a number greater than, or equal to, 0",
    "OTHER_LOAN_REPAYMENTS_REQUIRED": "Loan repayment is a required field",
    "OTHER_LOAN_REPAYMENTS_INVALID": "Loan repayment must be a number",
    "OTHER_LOAN_REPAYMENTS_MIN": "Loan repayment must be a number greater than, or equal to, 0",
    "OTHER_COURT_PAYMENTS_REQUIRED": "Court payments is a required field",
    "OTHER_COURT_PAYMENTS_INVALID": "Court payments must be a number",
    "OTHER_COURT_PAYMENTS_MIN": "Court payments must be a number greater than, or equal to, 0",
    "OTHER_CHILD_MAINTENANCE_REQUIRED": "Child maintenance is a required field",
    "OTHER_CHILD_MAINTENANCE_INVALID": "Child maintenance must be a number",
    "OTHER_CHILD_MAINTENANCE_MIN": "Child maintenance must be a number greater than, or equal to, 0"
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


def is_date_in_future(date):
    if date <= datetime.datetime.today().date():
        raise exceptions.ValidationError(ERROR_MESSAGES["HEARING_DATE_PASSED"])


def is_urn_not_used(urn):
    """
    Check that the urn hasn't already been used in a previous submission
    """

    if not Case.objects.can_use_urn(urn):
        raise exceptions.ValidationError(
            _(ERROR_MESSAGES['URN_ALREADY_USED']))

    return True


class RadioFieldRenderer(RadioFieldRenderer):
    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)

        context = {"id": id_, "renderer": self, "inputs": [force_text(widget) for widget in self]}

        return render_to_string("widgets/RadioSelect.html", context)


class DSRadioFieldRenderer(RadioFieldRenderer):
    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)

        context = {"id": id_, "renderer": self, "inputs": [force_text(widget) for widget in self]}

        return render_to_string("widgets/DSRadioSelect.html", context)


class HearingDateWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.TextInput(attrs={'maxlength': '2', 'pattern': '[0-9]+', 'class': 'form-control first-inline', 'size': '2'}),
                   forms.TextInput(attrs={'maxlength': '2', 'pattern': '[0-9]+', 'class': 'form-control', 'size': '2'}),
                   forms.TextInput(attrs={'maxlength': '4', 'pattern': '[0-9]+', 'class': 'form-control', 'size': '4'}),
                   ]
        super(HearingDateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            year, month, day = value.split("-")
            return [day, month, year]
        else:
            return ["", "", ""]

    def value_from_datadict(self, data, files, name):
        day, month, year = [widget.value_from_datadict(data, files, name + '_%s' % i) for i, widget in enumerate(self.widgets)]

        try:
            day = int(day)
        except (ValueError, TypeError):
            day = None

        try:
            month = int(month)
        except (ValueError, TypeError):
            try:
                month = datetime.datetime.strptime(month, "%b").month
            except (ValueError, TypeError):
                try:
                    month = datetime.datetime.strptime(month, "%B").month
                except (ValueError, TypeError):
                    month = None

        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None

        try:
            return str(datetime.date(day=day, month=month, year=year))
        except (ValueError, TypeError):
            return [widget.value_from_datadict(data, files, name + '_%s' % i) for i, widget in enumerate(self.widgets)]

    def format_output(self, rendered_widgets):
        return '/'.join(rendered_widgets)


class HearingDateField(forms.DateField):
    widget = HearingDateWidget


class URNWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.TextInput(attrs={'maxlength': '2', 'pattern': '[0-9]+', 'class': 'form-control first-inline', 'size': '2'}),
                   forms.TextInput(attrs={'maxlength': '2', 'class': 'form-control', 'size': '2'}),
                   forms.TextInput(attrs={'maxlength': '7', 'pattern': '[0-9]+', 'class': 'form-control', 'size': '7'}),
                   forms.TextInput(attrs={'maxlength': '2', 'pattern': '[0-9]+', 'class': 'form-control', 'size': '2'}),
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