from django import forms
from django.forms.widgets import Textarea


class BasePleaStepForm(forms.Form):
    pass
    # step_name = None

    # def save(self, request):
    #     assert self.step_name is not None, "step_name is not defined"
    #     plea = request.session.get('plea', {})
    #     plea[self.step_name] = self.cleaned_data
    #     request.session['plea'] = plea
    

class AboutForm(BasePleaStepForm):
    name = forms.CharField(max_length=255)
    date_of_hearing = forms.SplitDateTimeField()
    urn = forms.CharField(max_length=255)

class PleaInfoForm(BasePleaStepForm):
    mitigations = forms.CharField(widget=Textarea())
    guilty = forms.BooleanField()
    understand = forms.BooleanField()
    
