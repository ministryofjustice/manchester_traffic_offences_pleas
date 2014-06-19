import json

from django.core.mail import send_mail
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import TemplateView
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView

from . import forms

PLEA_FORMS = [
        ("about", forms.AboutForm),
        ("plea", forms.PleaInfoForm),
    ]
PLEA_TEMPLATES = {
    "about": "plea/about.html",
    "plea": "plea/plea.html",
}


class PleaForms(NamedUrlSessionWizardView):
    def get_template_names(self):
           return [PLEA_TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        # Send the email
        # TODO Extract this out properly.
        
        forms_dict_list = []
        for i, form in enumerate(form_list):
            forms_dict_list.append({
                PLEA_FORMS[i][0]: form.cleaned_data
            })
        
        send_mail(
            '[TEST] A plea has been submitted',
            json.dumps(forms_dict_list, cls=DjangoJSONEncoder),
            'sym.roe@digital.justice.gov.uk',
            ['manchesterteam+testplea@digital.justice.gov.uk'],
            fail_silently=False
        )

        return HttpResponseRedirect(reverse_lazy("complete_step"))

class CompleteStep(TemplateView):
    template_name = "plea/complete.html"

