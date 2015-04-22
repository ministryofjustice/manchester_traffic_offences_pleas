from collections import OrderedDict, namedtuple

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import NumberInput
from django.http import Http404, HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response


StageMessage = namedtuple("StageMessage", ["importance", "message", "tags"])


class FormStage(object):
    def __init__(self, all_urls=None, all_data=None):
        self.all_urls = all_urls
        self.all_data = all_data or {}
        self.forms = []
        self.next_step = ""
        self.context = {}
        self.messages = []

        if not hasattr(self, "dependencies"):
            self.dependencies = []

    def get_next(self, next_step):
        if next_step:
            return next_step

        current = self.all_urls.keys().index(self.name)
        if current <= len(self.all_urls.keys()):
            return self.all_urls.values()[current+1]

        return self.all_urls.values()[-1]

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

    def check_dependencies(self):
        for dependency in self.dependencies:
            if not (self.all_data[dependency].get("complete", False) is True):
                return False
        return True

    def add_message(self, importance, message, extra_tags=None):
        self.messages.append(StageMessage(importance=importance, message=message, tags=extra_tags))

    def load_forms(self, data=None, initial=False):
        if initial:
            initial_data = self.all_data.get(self.name, None)
            for form_class in self.form_classes:
                self.forms.append(form_class(initial=initial_data, label_suffix=""))
            return

        self.forms = [form(data, label_suffix="") for form in self.form_classes]

    def save_forms(self):
        form_data = {}
        for form in self.forms:
            form_data.update(form.cleaned_data)

        return form_data

    def load(self):
        self.load_forms(initial=True)

    def save(self, form_data, next_step=None):
        all_valid = True
        clean_data = {}

        if isinstance(form_data, QueryDict):
            form_data = {k: v for (k, v) in form_data.items()}

        self.load_forms(form_data)

        for form in self.forms:
            all_valid = form.is_valid() and all_valid

        if all_valid:
            clean_data.update(self.save_forms())
            clean_data["complete"] = True
            self.next_step = self.get_next(next_step)

        return clean_data

    def render(self, request_context):
        if self.next_step:
            return HttpResponseRedirect(self.next_step)
        else:
            context = self.context
            context.update({k: v for (k, v) in self.all_data.items()})
            context["forms"] = self.forms
            return render_to_response(self.template, context, request_context)


class MultiStageForm(object):
    def __init__(self, current_stage, url_name, storage_dict):
        self.urls = OrderedDict()
        self.current_stage_class = None
        self.current_stage = None
        self.storage_dict = storage_dict
        self.request_context = {}
        self.all_data = {}
        self.url_name = url_name

        for stage_class in self.stage_classes:
            self.urls[stage_class.name] = reverse(url_name, args=(stage_class.name,))
            self.all_data[stage_class.name] = {}
            if stage_class.name == current_stage:
                self.current_stage_class = stage_class

        self.load_from_storage(storage_dict)

        if self.current_stage_class is None:
            raise Http404

    def _get_stage_class(self, name):
        for stage_class in self.stage_classes:
            if stage_class.name == name:
                return stage_class

    def load_from_storage(self, storage_dict):
        # copy data out so we're not manipulating an external object
        self.all_data.update({key: val for (key, val) in storage_dict.items()})

    def save_to_storage(self):
        self.storage_dict.update({key: val for (key, val) in self.all_data.items()})

    def load(self, request_context):
        self.request_context = request_context
        self.current_stage = self.current_stage_class(self.urls, self.all_data)

        if not self.current_stage.check_dependencies():
            return HttpResponseRedirect(self.urls[self.stage_classes[0].name])

        self.current_stage.load()

    def save(self, form_data, request_context, next_step=None):
        self.request_context = request_context
        next_url = None
        if next_step:
            next_url = reverse(self.url_name, args=(next_step, ))

        self.current_stage = self.current_stage_class(self.urls, self.all_data)
        if self.current_stage.name not in self.all_data:
            self.all_data[self.current_stage.name] = {}

        self.all_data[self.current_stage.name].update(self.current_stage.save(form_data, next_step=next_url))
        self.save_to_storage()

        return True

    def process_messages(self, request):
        if self.current_stage is None:
            raise Exception("Current stage is not set")

        for msg in self.current_stage.messages:
            messages.add_message(request, msg.importance, msg.message, extra_tags=msg.tags)

    def render(self):
        return self.current_stage.render(self.request_context)


class GovUkDateWidget(SelectDateWidget):
    """
    Same as SelectDateWidget, but uses NumberInput rather than Select.
    """
    def create_select(self, name, field, value, val, choices):
        none_value = ""
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        if not self.is_required:
            choices.insert(0, none_value)
        local_attrs = self.build_attrs(id=field % id_)
        s = NumberInput()
        select_html = s.render(field % name, val, local_attrs)
        return select_html
