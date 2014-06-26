import smtplib
import socket

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
    ("review_send_error", forms.ReviewForm)
]

PLEA_TEMPLATES = {
    "about": "plea/about.html",
    "plea": "plea/plea.html",
    "review": "plea/review.html",
    "review_send_error": "plea/review_send_error.html"
}


class PleaForms(NamedUrlSessionWizardView):
    def get_template_names(self):
        return [PLEA_TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(PleaForms, self).get_context_data(form=form, **kwargs)
        if self.steps.current in ['review', 'review_send_error']:
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

    def render_done(self, form, **kwargs):
        final_form_list = []
        # walk through the form list and try to validate the data again.
        for form_key in self.get_form_list():
            form_obj = self.get_form(step=form_key,
                                     data=self.storage.get_step_data(form_key),
                                     files=self.storage.get_step_files(form_key))
            if not form_obj.is_valid():
                return self.render_revalidation_failure(form_key, form_obj, **kwargs)
            final_form_list.append(form_obj)

        try:
            done_response = self.done(final_form_list, **kwargs)
        except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
            return HttpResponseRedirect(reverse_lazy('plea_form_step', args=('review_send_error', )))
        else:
            self.storage.reset()
            return done_response
    
    def done(self, form_list, **kwargs):
        # Send the email
        context_data = {}

        for form in form_list:
            context_data.update(form.cleaned_data)

        send_plea_email(context_data)

        return HttpResponseRedirect(reverse_lazy("complete_step"))


class CompleteStep(TemplateView):
    template_name = "plea/complete.html"
