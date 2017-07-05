from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

from apps.forms.forms import (
    YESNO_CHOICES,
    to_bool,
    BaseStageForm,
    SplitStageForm,
)
from .fields import ERROR_MESSAGES


SATISFACTION_CHOICES = (
    (5, _("very satisfied")),
    (4, _("satisfied")),
    (3, _("neither satisfied nor dissatisfied")),
    (2, _("dissatisfied")),
    (1, _("very dissatisfied")))

RATING_QUESTIONS = {
    "overall": _("Overall, how satisfied were you with this service?"),
    "call-centre": _("Overall, how satisfied were you with the call centre?")
}


class ServiceForm(SplitStageForm):
    dependencies = {
        "call_centre_satisfaction": {
            "field": "used_call_centre",
            "value": True
        },
        "service_satisfaction": {
            "field": "used_call_centre"
        }
    }

    split_form_options = {
        "trigger": "used_call_centre",
        "nojs_only": True
    }

    used_call_centre = forms.TypedChoiceField(
        widget=RadioSelect(),
        required=True,
        choices=YESNO_CHOICES["Do/Naddo"],
        coerce=to_bool,
        label=_("Did you use the call centre to help you make your plea?"),
        error_messages={"required": ERROR_MESSAGES["USED_CALL_CENTRE_REQUIRED"]})

    call_centre_satisfaction = forms.ChoiceField(
        label=RATING_QUESTIONS["call-centre"],
        choices=SATISFACTION_CHOICES,
        required=True,
        error_messages={"required": ERROR_MESSAGES["CALL_CENTRE_SATISFACTION_REQUIRED"]},
        widget=RadioSelect())

    service_satisfaction = forms.ChoiceField(
        label=RATING_QUESTIONS["overall"],
        choices=SATISFACTION_CHOICES,
        required=True,
        error_messages={"required": ERROR_MESSAGES["SERVICE_SATISFACTION_REQUIRED"]},
        widget=RadioSelect())


class CommentsForm(BaseStageForm):
    comments = forms.CharField(
        label=_("If you have any further comments about this service, tell us here:"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 4,
                                     "cols": 50,
                                     "class": "form-control"}))

    email = forms.EmailField(
        label=_("Email address"),
        required=False,
        help_text=_("If you'd like us to get back to you, tell us your email address below:"),
        widget=forms.TextInput(attrs={"class": "form-control"}))
