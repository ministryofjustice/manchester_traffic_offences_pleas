from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import RequestContext, redirect
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from brake.decorators import ratelimit

from .models import CourtEmailCount, CourtEmailPlea

from apps.govuk_utils.forms import MultiStageForm
from stages import (CaseStage, YourDetailsStage, PleaStage, YourMoneyStage,
                    ReviewStage, CompleteStage)


class PleaOnlineForms(MultiStageForm):
    stage_classes = [CaseStage,
                     YourDetailsStage,
                     PleaStage,
                     YourMoneyStage,
                     ReviewStage,
                     CompleteStage]

    def __init__(self, *args):

        super(PleaOnlineForms, self).__init__(*args)

        self._urn_invalid = False

    def save(self, *args, **kwargs):
        """
        Check that the URN has not already been used.
        """

        try:
            saved_urn = self.all_data['case']['urn']
        except KeyError:
            saved_urn = None

        if saved_urn and not CourtEmailPlea.objects.can_use_urn(saved_urn):
            self._urn_invalid = True

            return

        super(PleaOnlineForms, self).save(*args, **kwargs)

    def render(self):
        if self._urn_invalid:
            return redirect('urn_already_used')

        return super(PleaOnlineForms, self).render()


class PleaOnlineViews(TemplateView):

    @never_cache
    def get(self, request, stage=None):
        if not stage:
            stage = PleaOnlineForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("plea_form_step", args=(stage,)))

        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        redirect = form.load(RequestContext(request))
        if redirect:
            return redirect

        form.process_messages(request)
        return form.render()

    @never_cache
    @method_decorator(ratelimit(block=True, rate="20/m"))
    def post(self, request, stage):
        nxt = request.GET.get("next", None)

        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        if form.save(request.POST, RequestContext(request), nxt):
            form.process_messages(request)
        return form.render()


class UrnAlreadyUsedView(TemplateView):
    template_name = "plea/urn_used.html"

    def post(self, request):

        request.session.flush()

        return redirect('plea_form_step', stage="case")
