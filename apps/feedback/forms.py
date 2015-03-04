from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

from apps.plea.fields import DSStackedRadioFieldRenderer

class FeedbackForm(forms.Form):
    SATISFACTION_CHOICES = (
        ("very satisfied", _("very satisfied")),
        ("satisfied", _("satisfied")),
        ("neither satisfied nor dissatisfied", _("neither satisfied nor dissatisfied")),
        ("dissatisfied", _("dissatisfied")),
        ("very dissatisfied", _("very dissatisfied")))

    feedback_email = forms.EmailField(label=_("Email address"),
    	                              required=False,
    	                              help_text=_("If you'd like us to get back to you, please leave your email address below."),
    	                              widget=forms.TextInput(attrs={"class": "form-control-wide"}))

    feedback_question = forms.CharField(label=_("Your feedback"),
    	                                required=True,
    	                                error_messages={"required": _("Please provide us with some feedback")},
    	                                widget=forms.Textarea(attrs={"rows": 5, 
    	                                                             "cols": 50, 
    	                                                             "class": "form-control-wide"}))

    feedback_satisfaction = forms.ChoiceField(label=_("Overall, how satisfied were you with this service?"),
                                     choices=SATISFACTION_CHOICES,
                                     required=False,
                                     widget=RadioSelect(renderer=DSStackedRadioFieldRenderer))