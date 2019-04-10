from django.forms import ModelForm, ChoiceField, Form
from ..plea.models import Court


# class SelectCourtForm(ModelForm):
#     class Meta:
#         model = Court
#         fields = ['court_name']

# class SelectCourtForm(Form):
#     CHOICES = (('Option 1', 'Option 1'), ('Option 2', 'Option 2'),)
#     field = ChoiceField(choices=CHOICES)
