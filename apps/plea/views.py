from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import RequestContext, redirect
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, FormView

from brake.decorators import ratelimit

from apps.govuk_utils.stages import MultiStageForm

from .models import Case, Court
from .forms import CourtFinderForm
from .stages import (CaseStage, YourDetailsStage, CompanyDetailsStage,
                    PleaStage, YourMoneyStage, YourExpensesStage,
                    CompanyFinancesStage, ReviewStage, CompleteStage)
from .fields import ERROR_MESSAGES


class PleaOnlineForms(MultiStageForm):
    stage_classes = [CaseStage,
                     YourDetailsStage,
                     CompanyDetailsStage,
                     PleaStage,
                     YourMoneyStage,
                     YourExpensesStage,
                     CompanyFinancesStage,
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
            saved_urn = self.all_data["case"]["urn"]
        except KeyError:
            saved_urn = None

        if saved_urn and not Case.objects.can_use_urn(saved_urn):
            self._urn_invalid = True

            return

        return super(PleaOnlineForms, self).save(*args, **kwargs)

    def render(self):
        if self._urn_invalid:
            return redirect("urn_already_used")

        return super(PleaOnlineForms, self).render()


class PleaOnlineViews(TemplateView):

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(PleaOnlineViews, self).dispatch(*args, **kwargs)

    def _get_storage(self, request):
        if not request.session.get("plea_data"):
            request.session["plea_data"] = {}

        return request.session["plea_data"]

    def _clear_storage(self, request):
        if "plea_data" in request.session:
            del request.session["plea_data"]

    def get(self, request, stage=None):
        storage = self._get_storage(request)

        if not stage:
            stage = PleaOnlineForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("plea_form_step", args=(stage,)))

        form = PleaOnlineForms(stage, "plea_form_step", storage)
        redirect = form.load(RequestContext(request))
        if redirect:
            return redirect

        form.process_messages(request)

        if stage == "complete":
            self._clear_storage(request)

        return form.render()

    @method_decorator(ratelimit(block=True, rate=settings.RATE_LIMIT))
    def post(self, request, stage):
        storage = self._get_storage(request)

        nxt = request.GET.get("next", None)

        form = PleaOnlineForms(stage, "plea_form_step", storage)
        form.save(request.POST, RequestContext(request), nxt)
        if not form._urn_invalid:
            form.process_messages(request)

        request.session.modified = True
        return form.render()


class UrnAlreadyUsedView(TemplateView):
    template_name = "urn_used.html"

    def post(self, request):

        del request.session["plea_data"]

        return redirect("plea_form_step", stage="case")


class CourtFinderView(FormView):
    template_name = "court_finder.html"
    form_class = CourtFinderForm

    def form_valid(self, form):
        try:
            court = Court.objects.get_by_urn(form.cleaned_data["urn"])
        except Court.DoesNotExist:
            court = False

        return self.render_to_response(self.get_context_data(form=form,
                                                             court=court,
                                                             submitted=True))

    def form_invalid(self, form):

        urn_is_invalid = False
        if "urn" in form.errors and ERROR_MESSAGES["URN_INCORRECT"] in form.errors["urn"]:
            urn_is_invalid = True

        return self.render_to_response(
            self.get_context_data(form=form,
                                  urn_is_invalid=urn_is_invalid))

