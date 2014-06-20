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
        ("review", forms.ReviewForm),
    ]
PLEA_TEMPLATES = {
    "about": "plea/about.html",
    "plea": "plea/plea.html",
    "review": "plea/review.html",
}


class PleaForms(NamedUrlSessionWizardView):
    def get_template_names(self):
           return [PLEA_TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(PleaForms, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'review':
            context.update({'all_data': self.get_all_cleaned_data()})
        
        if 'next' in self.request.GET:
            context.update({'next': self.request.GET['next']})
    
        return context
    
    def post(self, *args, **kwargs):
        next_form = super(PleaForms, self).post(*args, **kwargs)
        if 'next' in self.request.POST:
            if self.request.POST['next'] in self.get_form_list():
                next_url = self.get_step_url(self.request.GET['next'])
                return HttpResponseRedirect(next_url)
        return next_form
        
    
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

