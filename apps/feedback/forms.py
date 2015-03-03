from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import RadioSelect

from apps.plea.fields import DSStackedRadioFieldRenderer

class FeedbackForm(forms.Form):
    SATISFACTION_CHOICES = (
        ("very satisfied", "very satisfied"),
        ("satisfied", "satisfied"),
        ("neither satisfied nor dissatisfied", "neither satisfied nor dissatisfied"),
        ("dissatisfied", "dissatisfied"),
        ("very dissatisfied", "very dissatisfied"))

    feedback_email = forms.EmailField(label="Email address",
    	                              required=False,
    	                              help_text="If you'd like us to get back to you, please leave your email address below.",
    	                              widget=forms.TextInput(attrs={"class": "form-control-wide"}))

    feedback_question = forms.CharField(label="Your feedback",
    	                                required=True,
    	                                error_messages={"required": "Please provide us with some feedback"},
    	                                widget=forms.Textarea(attrs={"rows": 5, 
    	                                                             "cols": 50, 
    	                                                             "class": "form-control-wide"}))

    feedback_satisfaction = forms.ChoiceField(label="Overall, how satisfied were you with this service?",
                                     choices=SATISFACTION_CHOICES,
                                     required=False,
                                     widget=RadioSelect(renderer=DSStackedRadioFieldRenderer))