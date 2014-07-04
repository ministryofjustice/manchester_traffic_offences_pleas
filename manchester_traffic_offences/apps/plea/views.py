import smtplib
import socket

from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import RequestContext
from django.views.generic import TemplateView

from . import forms
from govuk_utils.forms import FormStage, MultiStageForm
from email import send_plea_email


class AboutStage(FormStage):
    name = "about"
    template = "plea/about.html"
    form_classes = [forms.AboutForm, ]


class PleaStage(FormStage):
    name = "plea"
    template = "plea/plea.html"
    form_classes = [forms.PleaInfoForm, ]


class ReviewStage(FormStage):
    name = "review"
    template = "plea/review.html"
    form_classes = []

    def save(self, form_data):
        response = super(ReviewStage, self).save(form_data)

        try:
            send_plea_email(self.form_data)
            next_step = reverse_lazy("plea_form_step", args=("complete", ))
        except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
            next_step = reverse_lazy('plea_form_step', args=('review_send_error', ))

        self.next = next_step
        return form_data


class ReviewSendErrorStage(FormStage):
    name = "send_error"
    template = "plea/review_send_error.html"
    form_classes = []


class CompleteStage(FormStage):
    name = "complete"
    template = "plea/complete.html"
    form_classes = []


class PleaOnlineForms(MultiStageForm):
    stage_classes = [AboutStage,
                     PleaStage,
                     ReviewStage,
                     ReviewSendErrorStage,
                     CompleteStage]


class PleaOnlineViews(TemplateView):
    def get(self, request, stage):
        print {k: v for k, v in request.session.items()}
        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        return form.load(RequestContext(request))

    def post(self, request, stage):
        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        return form.save(request.POST, RequestContext(request))





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
