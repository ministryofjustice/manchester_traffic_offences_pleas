import smtplib
import socket

from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
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
    form_classes = [forms.PleaInfoForm, forms.PleaForm]

    def load_forms(self, data=None, initial=False):
        count = self.all_data["about"].get("number_of_charges", 1)

        PleaForms = formset_factory(forms.PleaForm, extra=count)
        if initial:
            initial_plea_data = self.all_data[self.name].get("PleaForms", [])
            initial_info_data = self.all_data[self.name]
            self.forms.append(forms.PleaInfoForm(initial=initial_info_data))
            self.forms.append(PleaForms(initial=initial_plea_data))
        else:
            self.forms.append(forms.PleaInfoForm(data))
            self.forms.append(PleaForms(data))

    def save_forms(self):
        form_data = {}

        for form in self.forms:
            if hasattr(form, "management_form"):
                form_data["PleaForms"] = form.cleaned_data
            else:
                form_data.update(form.cleaned_data)

        return form_data


class ReviewStage(FormStage):
    name = "review"
    template = "plea/review.html"
    form_classes = []

    def save(self, form_data):
        response = super(ReviewStage, self).save(form_data)

        try:
            send_plea_email(self.all_data)
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
        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        return form.load(RequestContext(request))

    def post(self, request, stage):
        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        return form.save(request.POST, RequestContext(request))
