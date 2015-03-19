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

from .models import Case, Court


ERROR_MESSAGES = {
    "URN_REQUIRED": _("Enter your unique reference number (URN)"),
    "URN_INVALID": _("The unique reference number (URN) isn't valid. Enter the number exactly as it appears on page 1 of the pack"),
    "URN_ALREADY_USED": _("Enter the correct URN"),
    "HEARING_DATE_REQUIRED": _("Provide a court hearing date"),
    "HEARING_DATE_INVALID": _("The court hearing date isn't a valid format"),
    "HEARING_DATE_PASSED": _("The court hearing date must be after today"),
    "HEARING_DATE_INCORRECT": _("Enter the correct hearing date."),
    "NUMBER_OF_CHARGES_REQUIRED": _("Select the number of charges against you"),
    "ON_BEHALF_OF_COMPANY": _("Tell us if you're making a plea on behalf of a company"),
    "FULL_NAME_REQUIRED": _("Enter your full name"),
    "EMAIL_ADDRESS_REQUIRED": _("You must provide an email address"),
    "EMAIL_ADDRESS_INVALID": _("Email address isn't a valid format"),
    "CONTACT_NUMBER_REQUIRED": _("You must provide a contact number"),
    "CONTACT_NUMBER_INVALID": _("The contact number isn't a valid format"),
    "COMPANY_NAME_REQUIRED": _("Enter the company name"),
    "COMPANY_ADDRESS_REQUIRED": _("Enter the company address"),
    "NAME_REQUIRED": _("Tell us your name"),
    "POSITION_REQUIRED": _("Confirm your position in the company"),
    "COMPANY_CONTACT_NUMBER_REQUIRED": _("Enter a phone number so we can contact you about the company's plea"),
    "COMPANY_EMAIL_ADDRESS_REQUIRED": _("Enter an email address so we can contact you about the company's plea"),
    "PLEA_REQUIRED": _("Your plea must be selected"),
    "YOU_ARE_REQUIRED": _("You must let us know if you're employed, receiving benefits or other"),
    "EMPLOYERS_ADDRESS_REQUIRED": _("You must provide your employer's full address"),
    "PAY_PERIOD_REQUIRED": _("Tell us how often you get paid"),
    "PAY_AMOUNT_REQUIRED": _("Enter your take home pay"),
    "YOUR_JOB_REQUIRED": _("Tell us what your job is"),
    "BENEFITS_DETAILS_REQUIRED": _("Tell us which benefits you receive"),
    "BENEFITS_DEPENDANTS_REQUIRED": _("Tell us if this includes payment for dependants"),
    "HARDSHIP_REQUIRED": _("Tell us if paying a fine would cause you serious financial problems"),
    "UNDERSTAND_REQUIRED": _("You must confirm that you have read & understood the charge against you before you can submit your plea"),
    "OTHER_INFO_REQUIRED": _("Tell us how you earn your money"),
    "RECEIVE_EMAIL": _("You must choose whether you want to receive court correspondence through email"),
    "HARDSHIP_DETAILS_REQUIRED": _("You must tell us why paying a fine will cause you serious financial problems"),
    "OTHER_BILL_PAYERS_REQUIRED": _("You must tell us if anyone else contributes to your household bills."),
    "HOUSEHOLD_ACCOMMODATION_REQUIRED": _("Accommodation is a required field"),
    "HOUSEHOLD_ACCOMMODATION_INVALID": _("Accommodation must be a number"),
    "HOUSEHOLD_ACCOMMODATION_MIN": _("Accommodation must be a number greater than, or equal to, 0"),
    "HOUSEHOLD_UTILITY_BILLS_REQUIRED": _("Utility bills is a required field"),
    "HOUSEHOLD_UTILITY_BILLS_INVALID": _("Utility bills must be a number"),
    "HOUSEHOLD_UTILITY_BILLS_MIN": _("Utility bills must be a number greater than, or equal to, 0"),
    "HOUSEHOLD_INSURANCE_REQUIRED": _("Insurance is a required field"),
    "HOUSEHOLD_INSURANCE_INVALID": _("Insurance must be a number"),
    "HOUSEHOLD_INSURANCE_MIN": _("Insurance must be a number greater than, or equal to, 0"),
    "HOUSEHOLD_COUNCIL_TAX_REQUIRED": _("Council tax is a required field"),
    "HOUSEHOLD_COUNCIL_TAX_INVALID": _("Council tax must be a number"),
    "HOUSEHOLD_COUNCIL_TAX_MIN": _("Council tax must be a number greater than, or equal to, 0"),
    "OTHER_TV_SUBSCRIPTION_REQUIRED": _("TV subscription is a required field"),
    "OTHER_TV_SUBSCRIPTION_INVALID": _("TV subscription must be a number"),
    "OTHER_TV_SUBSCRIPTION_MIN": _("TV subscription must be a number greater than, or equal to, 0"),
    "OTHER_TRAVEL_EXPENSES_REQUIRED": _("Travel expenses is a required field"),
    "OTHER_TRAVEL_EXPENSES_INVALID": _("Travel expenses must be a number"),
    "OTHER_TRAVEL_EXPENSES_MIN": _("Travel expenses must be a number greater than, or equal to, 0"),
    "OTHER_TELEPHONE_REQUIRED": _("Telephone is a required field"),
    "OTHER_TELEPHONE_INVALID": _("Telephone must be a number"),
    "OTHER_TELEPHONE_MIN": _("Telephone must be a number greater than, or equal to, 0"),
    "OTHER_LOAN_REPAYMENTS_REQUIRED": _("Loan repayment is a required field"),
    "OTHER_LOAN_REPAYMENTS_INVALID": _("Loan repayment must be a number"),
    "OTHER_LOAN_REPAYMENTS_MIN": _("Loan repayment must be a number greater than, or equal to, 0"),
    "OTHER_COURT_PAYMENTS_REQUIRED": _("Court payments is a required field"),
    "OTHER_COURT_PAYMENTS_INVALID": _("Court payments must be a number"),
    "OTHER_COURT_PAYMENTS_MIN": _("Court payments must be a number greater than, or equal to, 0"),
    "OTHER_CHILD_MAINTENANCE_REQUIRED": _("Child maintenance is a required field"),
    "OTHER_CHILD_MAINTENANCE_INVALID": _("Child maintenance must be a number"),
    "OTHER_CHILD_MAINTENANCE_MIN": _("Child maintenance must be a number greater than, or equal to, 0"),
    "COMPANY_TRADING_PERIOD": _("You must tell us if the company has been trading for more than 12 months"),
    "COMPANY_NUMBER_EMPLOYEES": _("Enter the number of employees"),
    "COMPANY_GROSS_TURNOVER": _("Enter the company's gross turnover"),
    "COMPANY_NET_TURNOVER": _("Enter the company's net turnover"),
    "COMPANY_GROSS_TURNOVER_PROJECTED": _("Enter the company's projected gross turnover"),
    "COMPANY_NET_TURNOVER_PROJECTED": _("Enter the company's projected net turnover")
}


def is_urn_valid(urn):
    """
    URN is 11 or 13 characters long in the following format:

    00/AA/0000000/00
    or
    00/AA/00000/00
    """

    pattern = r"[0-9]{2}/[a-zA-Z]{2}/(?:[0-9]{5}|[0-9]{7})/[0-9]{2}"

    if not re.match(pattern, urn) or not Court.objects.has_court(urn):
        raise exceptions.ValidationError(_(ERROR_MESSAGES["URN_INVALID"]))

    return True


def is_date_in_future(date):
    if date <= datetime.datetime.today().date():
        raise exceptions.ValidationError(ERROR_MESSAGES["HEARING_DATE_PASSED"])

    return True


def is_date_within_range(date):

    if date > datetime.datetime.today().date()+datetime.timedelta(178):
        raise exceptions.ValidationError(ERROR_MESSAGES["HEARING_DATE_INCORRECT"])

    return True


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


class DSStackedRadioFieldRenderer(RadioFieldRenderer):
    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)

        context = {"id": id_, "renderer": self, "inputs": [force_text(widget) for widget in self]}

        return render_to_string("widgets/DSStackedRadioSelect.html", context)


class DSTemplateWidgetBase(forms.TextInput):
    template = ""

    def __init__(self, attrs=None, context=None):
        super(DSTemplateWidgetBase, self).__init__(attrs)
        self.context = context or {}

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        rendered_widget = super(DSTemplateWidgetBase, self).render(name, value, attrs)
        context = {"name": name, "value": value, "attrs": final_attrs, "field": rendered_widget}
        context.update(**self.context)
        return render_to_string(self.template, context)


class DSDateTemplateWidget(DSTemplateWidgetBase):
    template = "widgets/DSDateInputWidget.html"


class DSURNTemplateWidget(DSTemplateWidgetBase):
    template = "widgets/DSURNInputWidget.html"


class HearingDateWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [DSDateTemplateWidget(attrs={"pattern": "[0-9]*", "maxlength": "2", "size": "2", "class": "form-control-day"}, context={"title": "Day"}),
                   DSDateTemplateWidget(attrs={"pattern": "[0-9]*", "maxlength": "2", "size": "2", "class": "form-control-month"}, context={"title": "Month"}),
                   DSDateTemplateWidget(attrs={"pattern": "[0-9]*", "maxlength": "4", "size": "4", "class": "form-control-year"}, context={"title": "Year"}),
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

        if day == month == year == None:
            return ""

        try:
            return str(datetime.date(day=day, month=month, year=year))
        except (ValueError, TypeError):
            return [widget.value_from_datadict(data, files, name + "_%s" % i) for i, widget in enumerate(self.widgets)]

    def format_output(self, rendered_widgets):
        return '/'.join(rendered_widgets)


class HearingDateField(forms.DateField):
    widget = HearingDateWidget


class URNWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [DSURNTemplateWidget(attrs={"pattern": "[0-9]*", "maxlength": "2", "size": "2", "class": "form-control-urn-2"}, context={"title": "Part 1"}),
                   DSURNTemplateWidget(attrs={"pattern": "[A-Z]*", "maxlength": "2", "size": "2", "class": "form-control-urn-2"}, context={"title": "Part 2"}),
                   DSURNTemplateWidget(attrs={"pattern": "[0-9]*", "maxlength": "7", "size": "7", "class": "form-control-urn-7"}, context={"title": "Part 3"}),
                   DSURNTemplateWidget(attrs={"pattern": "[0-9]*", "maxlength": "2", "size": "2", "class": "form-control-urn-2"}, context={"title": "Part 4"}),
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

    #default_validators = [is_urn_valid]
    widget = URNWidget()
