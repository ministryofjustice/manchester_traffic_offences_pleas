from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView

from . import forms
from email import send_plea_email

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
        context_data = {}

        for form in form_list:
            context_data.update(form.cleaned_data)

        send_plea_email(context_data)

        return HttpResponseRedirect(reverse_lazy("complete_step"))


class CompleteStep(TemplateView):
    template_name = "plea/complete.html"

