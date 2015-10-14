from brake.decorators import ratelimit

from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import RequestContext

from apps.forms.stages import MultiStageForm
from apps.forms.views import StorageView
from .stages import ServiceStage, CommentsStage, CompleteStage


class FeedbackForms(MultiStageForm):
    stage_classes = [ServiceStage,
                     CommentsStage,
                     CompleteStage]


class FeedbackViews(StorageView):

    def get(self, request, stage=None):
        storage = self._get_storage(request, "feedback_data")

        kw_args = {k: v for (k, v) in request.GET.items()}
        if request.GET.get("next"):
            nxt = kw_args.pop("next")
            if kw_args:
                redirect_url = reverse(nxt, kwargs=kw_args)
            else:
                redirect_url = reverse(nxt)

            storage["feedback_redirect"] = redirect_url

        if not storage.get("user_agent"):
            storage["user_agent"] = request.META["HTTP_USER_AGENT"]

        if not stage:
            stage = FeedbackForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("feedback_form_step", args=(stage,)))

        form = FeedbackForms(stage, "feedback_form_step", storage)
        redirect = form.load(RequestContext(request))
        if redirect:
            return redirect

        form.process_messages(request)

        if stage == "complete":
            redirect_url = storage.get("feedback_redirect", "/")
            self._clear_storage(request, "feedback_data")
            return HttpResponseRedirect(redirect_url)

        return form.render()

    @method_decorator(ratelimit(block=True, rate=settings.RATE_LIMIT))
    def post(self, request, stage):
        storage = self._get_storage(request, "feedback_data")

        nxt = request.GET.get("next", None)

        form = FeedbackForms(stage, "feedback_form_step", storage)
        form.save(request.POST, RequestContext(request), nxt)
        form.process_messages(request)
        request.session.modified = True

        return form.render()
