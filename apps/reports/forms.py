from django.forms import ModelForm
from ..plea.models import Court


class SelectCourtForm(ModelForm):
    class Meta:
        model = Court
        fields = ['court_name']
