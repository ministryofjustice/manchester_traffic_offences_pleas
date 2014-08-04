from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import NumberInput
from django.http import Http404, HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response


class FormStage(object):
    def __init__(self, all_urls=None, all_data=None):
        self.all_urls = all_urls
        self.all_data = all_data or {}
        self.forms = []
        self.next = ""
        self.context = {}

    def get_next(self, next):
        if next:
            return next

        current = self.all_urls.keys().index(self.name)
        if current <= len(self.all_urls.keys()):
            return self.all_urls.values()[current+1]

        return self.all_urls.values()[-1]

    def load_forms(self, data=None, initial=False):
        if initial:
            initial_data = self.all_data.get(self.name, None)
            for form_class in self.form_classes:
                self.forms.append(form_class(initial=initial_data))
            return

        self.forms = [form(data) for form in self.form_classes]

    def save_forms(self):
        form_data = {}
        for form in self.forms:
            form_data.update(form.cleaned_data)

        return form_data

    def load(self):
        self.load_forms(initial=True)

    def save(self, form_data, next=None):
        all_valid = True
        clean_data = {}

        if isinstance(form_data, QueryDict):
            form_data = {k: v for (k, v) in form_data.items()}

        self.load_forms(form_data)

        for form in self.forms:
            all_valid = form.is_valid() and all_valid

        if all_valid:
            clean_data.update(self.save_forms())
            self.next = self.get_next(next)

        return clean_data

    def render(self, request_context):
        if self.next:
            return HttpResponseRedirect(self.next)
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
        # TODO validate previous stages?
        self.current_stage = self.current_stage_class(self.urls, self.all_data)
        self.current_stage.load()
        return self.current_stage.render(request_context)

    def save(self, form_data, request_context, next=None):
        next_url = None
        if next:
            next_url = reverse(self.url_name, args=(next, ))

        self.current_stage = self.current_stage_class(self.urls, self.all_data)
        if self.current_stage.name not in self.all_data:
            self.all_data[self.current_stage.name] = {}
        self.all_data[self.current_stage.name].update(self.current_stage.save(form_data, next=next_url))
        self.save_to_storage()
        return self.current_stage.render(request_context)


class GovUkDateWidget(SelectDateWidget):
    """
    Same as SelectDateWidget, but uses NumberInput rather than Select.
    """
    def create_select(self, name, field, value, val, choices):
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
