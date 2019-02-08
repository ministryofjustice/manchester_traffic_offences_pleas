
from apps.plea.models import CaseTracker, Case

from collections import OrderedDict, namedtuple

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, QueryDict
from django.shortcuts import render
import logging
logger = logging.getLogger(__name__)

StageMessage = namedtuple("StageMessage", ["importance", "message", "tags"])


class FormStage(object):
    def __init__(self, all_urls=None, all_data=None):
        self.all_urls = all_urls
        self.all_data = all_data or {}
        self.form = None
        self.next_step = ""
        self.context = {}
        self.messages = []
        self.stage_completion = None

        if not hasattr(self, "storage_key"):
            self.storage_key = self.name

        if not hasattr(self, "dependencies"):
            self.dependencies = []

    def set_session_timeout(self, timeout):
        self.context.update({"sessionTimeout": timeout})

    def get_next(self, next_step):
        if next_step:
            return next_step
        url_keys = list(self.all_urls.keys())
        current = url_keys.index(self.name)
        url_values = list(self.all_urls.values())
        if current <= len(url_keys):
            return url_values[current+1]

        return url_values[-1]

    def set_next_step(self, next_step, skip=None):
        """
        A convenience function to set the next form stage and optionally
        skip stages by marking them as completed.
        """

        self.next_step = self.all_urls[next_step]

        data = self.all_data.get(next_step, None)

        if data and 'skipped' in data:
            del data['skipped']

        if skip:
            for stage in skip:
                self.all_data[stage]['complete'] = True
                self.all_data[stage]['skipped'] = True

    def check_dependencies_are_complete(self):
        for dependency in self.dependencies:
            if "data" in self.all_data[dependency]:
                for data in self.all_data[dependency]["data"]:
                    if data.get("complete", False) is not True:
                        return False
            elif self.all_data[dependency].get("complete", False) is not True:
                return False
        return True

    def add_message(self, importance, message, extra_tags=None):
        self.messages.append(StageMessage(importance=importance, message=message, tags=extra_tags))

    def load_forms(self, data=None, initial=False):
        if initial:
            initial_data = self.all_data.get(self.storage_key, None)
            if self.form_class:
                self.form = self.form_class(initial=initial_data, label_suffix="")
            return

        if self.form_class:
            self.form = self.form_class(data, label_suffix="")

    def save_forms(self):
        form_data = {}
        form_data.update(self.form.cleaned_data)

        return form_data

    def load(self, request_context=None):
        # Reset split_form state if returning to trigger question
        if hasattr(request_context, "request") and ("reset" in request_context.request.GET):

            try:
                self.all_data[self.storage_key].get("data")[self.index - 1].pop("split_form", None)
            except AttributeError:
                self.all_data[self.storage_key].pop("split_form", None)

        self.load_forms(initial=True)

    def save(self, form_data, next_step=None):
        clean_data = {}
        if isinstance(form_data, QueryDict):
            form_data = {k: v for (k, v) in form_data.items()}
        self.load_forms(form_data)
        self.split_form = form_data.get("split_form", None)
        clean_data["split_form"] = self.split_form

        if self.form and self.form.is_valid():
            clean_data.update(self.save_forms())

            if self.split_form is None or self.split_form == "split_form_last_step":
                clean_data["complete"] = True
                self.next_step = self.get_next(next_step)
            else:
                self.all_data[self.storage_key].pop("complete", None)
                self.form.data["split_form"] = "split_form_last_step"
                clean_data["split_form"] = "split_form_last_step"

        return clean_data

    def render(self, request, request_context):
        if self.next_step:
            return HttpResponseRedirect(self.next_step)
        else:
            context = self.context
            context.update({k: v for (k, v) in self.all_data.items()})
            context["form"] = self.form
            return render(request, self.template, context)


class IndexedStage(FormStage):
    def __init__(self, all_urls=None, all_data=None, index=None):
        self.index = index or 1
        super(IndexedStage, self).__init__(all_urls, all_data)

    def load(self, request_context):
        if self.index is None:
            return HttpResponseRedirect(self.all_urls[self.name])
        else:
            return super(IndexedStage, self).load(request_context)


class MultiStageForm(object):
    url_name = ""

    def __init__(self, storage_dict, current_stage, index=None):
        self.urls = OrderedDict()
        self.current_stage_class = None
        self.current_stage = None
        self.storage_dict = storage_dict
        self.request_context = {}
        self.all_data = {}
        self.index = index

        for stage_class in self.stage_classes:
            if issubclass(stage_class, IndexedStage):
                self.urls[stage_class.name] = reverse(self.url_name, kwargs={"stage": stage_class.name,
                                                                             "index": self.index or 1})
            else:
                self.urls[stage_class.name] = reverse(self.url_name, args=(stage_class.name,))

            try:
                self.all_data[stage_class.storage_key] = {}
            except AttributeError:
                self.all_data[stage_class.name] = {}

            if stage_class.name == current_stage:
                self.current_stage_class = stage_class

        if self.current_stage_class is None:
            raise Http404("Stage not set")

        self.load_from_storage(storage_dict)

    def _get_stage_class(self, name):
        for stage_class in self.stage_classes:
            if stage_class.name == name:
                return stage_class

    def load_from_storage(self, storage_dict):
        # copy data out so we're not manipulating an external object
        self.all_data.update({key: val for (key, val) in storage_dict.items()})
        if not self.current_stage_class.name == "enter_urn":
            try:
                urn = self.all_data['case'].get('urn', None)
                CaseTracker.objects.update_stage_for_urn(urn, self.current_stage_class.__name__)
            except Exception:
                # Catching the top level exception as don't want to risk the main process being affected
                pass

    def save_to_storage(self):
        self.storage_dict.update({key: val for (key, val) in self.all_data.items()})

    def load(self, request_context):
        self.request_context = request_context

        if issubclass(self.current_stage_class, IndexedStage):
            self.current_stage = self.current_stage_class(self.urls, self.all_data, self.index)
        else:
            self.current_stage = self.current_stage_class(self.urls, self.all_data)

        if not self.current_stage.name == "enter_urn":
            if not self.all_data.get("welsh_court", False):
                self.all_data["disable_language_switch"] = True
        if not self.current_stage.check_dependencies_are_complete():
            if self.current_stage.name == "complete":
                logger.error('User redirected from complete to start page due to lack of data', exc_info=False, extra={
                    # Optionally pass a request and we'll grab any information we can
                    'request_context': request_context,
                    'form': self,
                })
                redirect = "/"
            else:
                redirect = self.urls[self.stage_classes[0].name]

            return HttpResponseRedirect(redirect)
        return self.current_stage.load(request_context)

    def save(self, form_data, request_context, next_step=None):
        self.request_context = request_context
        next_url = None
        if next_step:
            next_url = reverse(self.url_name, args=(next_step, ))

        if issubclass(self.current_stage_class, IndexedStage):
            self.current_stage = self.current_stage_class(self.urls, self.all_data, self.index)
        else:
            self.current_stage = self.current_stage_class(self.urls, self.all_data)

        if self.current_stage.storage_key not in self.all_data:
            self.all_data[self.current_stage.storage_key] = {}

        self.all_data[self.current_stage.storage_key].update(self.current_stage.save(form_data, next_step=next_url))
        self.save_to_storage()

        return True

    def process_messages(self, request):
        if self.current_stage is None:
            raise Exception("Current stage is not set")

        for msg in self.current_stage.messages:
            messages.add_message(request, msg.importance, msg.message, extra_tags=msg.tags)

    def render(self, request, request_context=None):
        if request_context is None:
            request_context = self.request_context
        return self.current_stage.render(request, request_context)
