import json

from django.core.mail import send_mail
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy

from django.views.generic import FormView
from django.views.generic import TemplateView

from . import forms

class BaseStepFormView(FormView):
    def form_valid(self, form):
        form.save(self.request)
        return super(BaseStepFormView, self).form_valid(form)
    
    def get_initial(self):
        plea = self.request.session.get('plea', {})
        if self.form_class.step_name in plea:
            return plea[self.form_class.step_name]

class ExampleStep(BaseStepFormView):
    template_name = "plea/example.html"
    form_class = forms.ExampleStep
    step_name = "example"
    success_url = reverse_lazy('review_step')

class ReviewStep(TemplateView):
    template_name = "plea/review.html"
    
class CompleteStep(TemplateView):
    http_method_names = ['post',]
    template_name = "plea/complete.html"
    
    def post(self, request, *args, **kwargs):
        # Send the email
        # TODO Extract this out properly.
        send_mail(
            '[TEST] A plea has been submitted',
            json.dumps(self.request.session['plea']),
            'sym.roe@digital.justice.gov.uk',
            ['manchesterteam@digital.justice.gov.uk'],
            fail_silently=False
        )
        del self.request.session['plea']
        return self.get(request)