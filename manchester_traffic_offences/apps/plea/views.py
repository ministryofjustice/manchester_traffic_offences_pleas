from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import RequestContext
from django.views.generic import TemplateView

from .forms import PleaOnlineForms


class PleaOnlineViews(TemplateView):
    def get(self, request, stage=None):

        if not stage:
            stage = PleaOnlineForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("plea_form_step", args=(stage,)))

        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        return form.load(RequestContext(request))

    def post(self, request, stage):
        next = request.GET.get("next", None)
        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        return form.save(request.POST, RequestContext(request), next)
