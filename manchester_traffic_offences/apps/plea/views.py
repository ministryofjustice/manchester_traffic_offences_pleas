from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import RequestContext
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from brake.decorators import ratelimit

from govuk_utils.forms import MultiStageForm
from stages import (CaseStage, YourDetailsStage, PleaStage, YourMoneyStage,
                    ReviewStage, ReviewSendErrorStage, CompleteStage)


class PleaOnlineForms(MultiStageForm):
    stage_classes = [CaseStage,
                     YourDetailsStage,
                     PleaStage,
                     YourMoneyStage,
                     ReviewStage,
                     ReviewSendErrorStage,
                     CompleteStage]


class PleaOnlineViews(TemplateView):
    @never_cache
    def get(self, request, stage=None):
        if not stage:
            stage = PleaOnlineForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("plea_form_step", args=(stage,)))

        form = PleaOnlineForms(stage, "plea_form_step", request.session)

        return form.load(RequestContext(request))

    @method_decorator(ratelimit(block=True, rate="10/m"))
    def post(self, request, stage):
        nxt = request.GET.get("next", None)
        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        response = form.save(request.POST, RequestContext(request), nxt)
        return response
