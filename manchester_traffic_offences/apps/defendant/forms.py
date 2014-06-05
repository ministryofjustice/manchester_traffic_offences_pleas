from django import forms

from .models import Defendant

class DefendantLoginForm(forms.ModelForm):
    class Meta:
        model = Defendant
        fields = ["urn",]
    