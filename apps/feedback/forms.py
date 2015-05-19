from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

from apps.plea.fields import DSStackedRadioFieldRenderer

SATISFACTION_CHOICES = (
    (5, _("very satisfied")),
    (4, _("satisfied")),
    (3, _("neither satisfied nor dissatisfied")),
    (2, _("dissatisfied")),
    (1, _("very dissatisfied")))


class FeedbackForm(forms.Form):

    feedback_email = forms.EmailField(
        label=_("Email address"),
        required=False,
        help_text=_("If you'd like us to get back to you, please leave your email address below."),
        widget=forms.TextInput(attrs={"class": "form-control-wide"}))

    feedback_question = forms.CharField(
        label=_("Your feedback"),
        required=True,
        error_messages={"required": _("Please provide us with some feedback")},
        widget=forms.Textarea(attrs={"rows": 5,
                                     "cols": 50,
                                     "class": "form-control-wide"}))

    feedback_satisfaction = forms.ChoiceField(
        label=_("Overall, how satisfied were you with this service?"),
        choices=SATISFACTION_CHOICES,
        required=True,
        error_messages={"required": _("Please select one of the options below")},
        widget=RadioSelect(renderer=DSStackedRadioFieldRenderer))