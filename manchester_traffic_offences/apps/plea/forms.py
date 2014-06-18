from django import forms


class BasePleaStepForm(forms.Form):
    step_name = None

    def save(self, request):
        assert self.step_name is not None, "step_name is not defined"
        plea = request.session.get('plea', {})
        plea[self.step_name] = self.cleaned_data
        request.session['plea'] = plea
    
class ExampleStep(BasePleaStepForm):
    step_name = "example"
    subject = forms.CharField(max_length=100)