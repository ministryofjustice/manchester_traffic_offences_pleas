from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import RequestContext
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from brake.decorators import ratelimit

from rest_framework.views import APIView
from rest_framework.response import Response
from dateutil.parser import parse

from .models import CourtEmailCount

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


class PleaOnlineViews(TemplateView):
    @never_cache
    def get(self, request, stage=None):
        if not stage:
            stage = PleaOnlineForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("plea_form_step", args=(stage,)))

        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        form.load(RequestContext(request))
        form.process_messages(request)
        return form.render()

    @never_cache
    @method_decorator(ratelimit(block=True, rate="20/m"))
    def post(self, request, stage):
        nxt = request.GET.get("next", None)

        form = PleaOnlineForms(stage, "plea_form_step", request.session)
        form.save(request.POST, RequestContext(request), nxt)
        form.process_messages(request)
        return form.render()


class StatsBasicView(APIView):

    def get(self, request):
        stats = CourtEmailCount.objects.get_stats()

        return Response(stats)


class StatsByHearingDateView(APIView):

    def get(self, request):

        stats = CourtEmailCount.objects.get_stats_by_hearing_date()

        return Response(stats)
