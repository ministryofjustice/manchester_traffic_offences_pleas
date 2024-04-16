from brake.decorators import ratelimit

from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext

from apps.forms.stages import MultiStageForm
from apps.forms.views import StorageView
from .stages import ServiceStage, CommentsStage, CompleteStage


class FeedbackForms(MultiStageForm):
    url_name = "feedback_form_step"
    stage_classes = [ServiceStage,
                     CommentsStage,
                     CompleteStage]


class FeedbackViews(StorageView):
    start = "service"

    def __init__(self, *args, **kwargs):
        super(FeedbackViews, self).__init__(*args, **kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        self.storage = self.get_storage(request, "feedback_data")

        self.redirect_url = self.storage.get("feedback_redirect", "/")

        # If the session has timed out, redirect to start page
        if not request.session.get("feedback_data") and kwargs.get("stage", self.start) != self.start:
            return HttpResponseRedirect(self.redirect_url)

        return super(FeedbackViews, self).dispatch(request, *args, **kwargs)

    def get(self, request, stage=None):
        kw_args = {k: v for (k, v) in request.GET.items()}
        if request.GET.get("next"):
            nxt = kw_args.pop("next")
            if kw_args:
                redirect_url = reverse(nxt, kwargs=kw_args)

                try:
                    if kw_args["stage"] == "complete":
                        redirect_url = "/"
                except KeyError:
                    pass
            else:
                if nxt == "plea_form_step":
                    nxt = "plea_form"
                redirect_url = reverse(nxt)

            self.storage["feedback_redirect"] = redirect_url

        if not self.storage.get("user_agent"):
            self.storage["user_agent"] = request.META["HTTP_USER_AGENT"]

        if not stage:
            stage = FeedbackForms.stage_classes[0].name
            return HttpResponseRedirect(reverse_lazy("feedback_form_step", args=(stage,)))

        form = FeedbackForms(self.storage, stage)
        redirect = form.load(RequestContext(request))
        if redirect:
            return redirect

        form.process_messages(request)

        if stage == "complete":
            self.clear_storage(request, "feedback_data")

        return form.render(request)

    @method_decorator(ratelimit(block=True, rate=settings.RATE_LIMIT))
    def post(self, request, stage):
        nxt = request.GET.get("next", None)

        form = FeedbackForms(self.storage, stage)
        form.save(request.POST, RequestContext(request), nxt)
        form.process_messages(request)
        request.session.modified = True

        return form.render(request)
