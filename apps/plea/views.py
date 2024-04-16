import datetime
import json

from brake.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView
from django.template import RequestContext
import logging
logger = logging.getLogger(__name__)
from django.contrib.admin.views.decorators import staff_member_required

from apps.forms.stages import MultiStageForm
from apps.forms.views import StorageView
from make_a_plea.helpers import (
    filter_cases_by_month,
    get_supported_language_from_request,
    parse_date_or_400,
    staff_or_404,
)
from .models import Case, Court, CaseTracker
from .forms import CourtFinderForm
from .stages import (URNEntryStage,
                     AuthenticationStage,
                     NoticeTypeStage,
                     CaseStage,
                     YourDetailsStage,
                     CompanyDetailsStage,
                     PleaStage,
                     YourStatusStage,
                     YourEmploymentStage,
                     YourSelfEmploymentStage,
                     YourOutOfWorkBenefitsStage,
                     AboutYourIncomeStage,
                     YourBenefitsStage,
                     YourPensionCreditStage,
                     YourIncomeStage,
                     HardshipStage,
                     HouseholdExpensesStage,
                     OtherExpensesStage,
                     CompanyFinancesStage,
                     ReviewStage,
                     CompleteStage)
from .fields import ERROR_MESSAGES




class PleaOnlineForms(MultiStageForm):
    url_name = "plea_form_step"
    stage_classes = [URNEntryStage,
                     AuthenticationStage,
                     NoticeTypeStage,
                     CaseStage,
                     YourDetailsStage,
                     CompanyDetailsStage,
                     PleaStage,
                     YourStatusStage,
                     YourEmploymentStage,
                     YourSelfEmploymentStage,
                     YourOutOfWorkBenefitsStage,
                     AboutYourIncomeStage,
                     YourBenefitsStage,
                     YourPensionCreditStage,
                     YourIncomeStage,
                     HardshipStage,
                     HouseholdExpensesStage,
                     OtherExpensesStage,
                     CompanyFinancesStage,
                     ReviewStage,
                     CompleteStage]

    def __init__(self, *args, **kwargs):
        super(PleaOnlineForms, self).__init__(*args, **kwargs)

        self._urn_invalid = False

    def save(self, *args, **kwargs):
        """
        Check that the URN has not already been used.
        """
        saved_urn = self.all_data.get("case", {}).get("urn")
        saved_first_name = self.all_data.get("your_details", {}).get("first_name")
        saved_last_name = self.all_data.get("your_details", {}).get("last_name")
        if all([
                saved_urn,
                saved_first_name,
                saved_last_name,
                not Case.objects.can_use_urn(saved_urn, saved_first_name, saved_last_name)
        ]):
            self._urn_invalid = True
        else:
            return super(PleaOnlineForms, self).save(*args, **kwargs)

    def render(self, request, request_context=None):
        request_context = request_context if request_context else {}
        if self._urn_invalid:
            return redirect("urn_already_used")

        return super(PleaOnlineForms, self).render(request)


class PleaOnlineViews(StorageView):
    start = "enter_urn"

    def __init__(self, *args, **kwargs):
        super(PleaOnlineViews, self).__init__(*args, **kwargs)
        self.index = None
        self.storage = None

    def dispatch(self, request, *args, **kwargs):
        # If the session has timed out, redirect to start page
        if all([
                not request.session.get("plea_data"),
                kwargs.get("stage", self.start) != self.start,
        ]):

            return HttpResponseRedirect("/")


        # Store the index if we've got one
        idx = kwargs.pop("index", None)
        try:
            self.index = int(idx)
        except (ValueError, TypeError):
            self.index = 0

        # Load storage
        self.storage = self.get_storage(request, "plea_data")
        return super(PleaOnlineViews, self).dispatch(request, *args, **kwargs)

    def get(self, request, stage=None):
        if not stage:
            stage = PleaOnlineForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("plea_form_step", args=(stage,)))

        form = PleaOnlineForms(self.storage, stage, self.index)

        case_redirect = form.load(RequestContext(request))
        if case_redirect:
            return case_redirect

        form.process_messages(request)

        if stage == "complete":
            self.clear_storage(request, "plea_data")

        return form.render(request)

    @method_decorator(ratelimit(block=True, rate=settings.RATE_LIMIT))
    def post(self, request, stage):
        nxt = request.GET.get("next", None)

        form = PleaOnlineForms(self.storage, stage, self.index)
        form.save(request.POST, RequestContext(request), nxt)

        if not form._urn_invalid:
            form.process_messages(request)

        request.session.modified = True
        return form.render(request)

    def render(self, request, request_context=None):
        request_context = request_context if request_context else {}
        return super(PleaOnlineViews, self).render(request)


class UrnAlreadyUsedView(StorageView):
    template_name = "urn_used.html"

    def post(self, request):

        del request.session["plea_data"]

        return redirect("plea_form_step", stage="case")


class CourtFinderView(FormView):
    template_name = "court_finder.html"
    form_class = CourtFinderForm

    def form_valid(self, form):
        try:
            court = Court.objects.get_court_dx(form.cleaned_data["urn"])
        except Court.DoesNotExist:
            court = False

        return self.render_to_response(
            self.get_context_data(
                form=form,
                court=court,
                submitted=True,
            )
        )



@staff_or_404
def stats(request):
    """
    Generate usage statistics (optionally by language) and send via email
    """

    filter_params = {
        "sent": True,
        "language": get_supported_language_from_request(request),
    }
    if "end_date" in request.GET:
        end_date = parse_date_or_400(request.GET["end_date"])
    else:
        now = datetime.datetime.utcnow()
        last_day_of_last_month = now - datetime.timedelta(days=now.day)
        end_date = datetime.datetime(
            last_day_of_last_month.year,
            last_day_of_last_month.month,
            last_day_of_last_month.day,
            23, 59, 59)
    filter_params["completed_on__lte"] = end_date

    if "start_date" in request.GET:
        start_date = parse_date_or_400(request.GET["start_date"])
    else:
        start_date = datetime.datetime(1970, 1, 1)
    filter_params["completed_on__gte"] = start_date

    journies = Case.objects.filter(**filter_params).order_by("completed_on")
    count = journies.count()
    journies_by_month = filter_cases_by_month(journies)

    earliest_journey = journies[0] if journies else None
    latest_journey = journies.reverse()[0] if journies else None

    response = {
        "summary": {
            "language": filter_params["language"],
            "total": count,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "earliest_journey": earliest_journey.completed_on.isoformat() if earliest_journey else None,
            "latest_journey": latest_journey.completed_on.isoformat() if latest_journey else None,
            "by_month": journies_by_month,
        },
        "latest_example": {
            "urn": latest_journey.urn,
            "name": latest_journey.name,
            "extra_data": {
                k: v
                for k, v in latest_journey.extra_data.items()
                if k in [
                    "Forename1",
                    "Forename2",
                    "Surname",
                    "DOB",
                ]
            },
        }
    } if count else {}

    return HttpResponse(
        json.dumps(response, indent=4),
        content_type="application/json",
    )

