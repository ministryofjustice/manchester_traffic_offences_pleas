from django import forms
from django.forms.widgets import Textarea, RadioSelect

from govuk_utils.forms import GovUkDateWidget
from defendant.utils import is_valid_urn_format

class URNField(forms.CharField):
    default_validators = [is_valid_urn_format, ]

class BasePleaStepForm(forms.Form):
    """
    Note that names in these forms can't be the same, otherwise they will get 
    merged in to the last value used.
    """
    pass

class AboutForm(BasePleaStepForm):
    date_of_hearing = forms.DateField(widget=GovUkDateWidget())
    urn = URNField(max_length=255)
    name = forms.CharField(max_length=255)

class PleaInfoForm(BasePleaStepForm):
    
    PLEA_CHOICES = (
        ('guilty', 'Guilty'),
        ('not_guilty', 'Not Guilty'),
        ('both', 'Both'),
    )
    
    guilty = forms.ChoiceField(choices=PLEA_CHOICES, widget=RadioSelect())
    mitigations = forms.CharField(widget=Textarea())
    understand = forms.BooleanField()

class ReviewForm(BasePleaStepForm):
    # Left blank for now, as this isn't a real form.
    pass