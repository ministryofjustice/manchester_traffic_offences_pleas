from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import NumberInput
from django.http import Http404, HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response


class FormStage(object):
    """

    """
    def __init__(self, all_urls=None, form_data=None):
        self.all_urls = all_urls
        self.form_data = form_data or {}
        self.forms = []
        self.next = ""

    def get_next(self):
        current = self.all_urls.keys().index(self.name)
        if current <= len(self.all_urls.keys()):
            return self.all_urls.values()[current+1]

        return self.all_urls.values()[-1]

    def load_forms(self, data=None):
        self.forms = [form(data) for form in self.form_classes]

    def load(self):
        self.load_forms()

    def save(self, form_data):
        clean_data = {}
        all_valid = True

        if isinstance(form_data, QueryDict):
            form_data = {k: v for (k, v) in form_data.items()}

        self.load_forms(form_data)

        for form in self.forms:
            if form.is_valid():
                if hasattr(form, "management_form"):
                    for fdata in form.cleaned_data:
                        clean_data.update(fdata)
                        continue

                clean_data.update(form.cleaned_data)
            else:
                all_valid = False

        if all_valid:
            form_data.update(clean_data)
            self.next = self.get_next()

        return form_data

    def render(self, request_context):
        if self.next:
            return HttpResponseRedirect(self.next)
        else:
            context = {k: v for (k, v) in self.form_data.items()}
            context["forms"] = self.forms
            return render_to_response(self.template, context, request_context)


class MultiStageForm(object):
    def __init__(self, current_stage, url_name, storage_dict):
        self.urls = OrderedDict()
        self.current_stage_class = None
        self.storage_dict = storage_dict
        self.form_data = {}

        for stage_class in self.stage_classes:
            self.urls[stage_class.name] = reverse(url_name, args=(stage_class.name,))
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
        self.form_data = {key: val for (key, val) in storage_dict.items()}

    def save_to_storage(self):
        self.storage_dict.update({key: val for (key, val) in self.form_data.items()})

    def load(self, request_context):
        # TODO validate previous stages?
        stage = self.current_stage_class(self.urls, self.form_data)
        stage.load()
        return stage.render(request_context)

    def save(self, form_data, request_context):
        stage = self.current_stage_class(self.urls, self.form_data)
        self.form_data.update(stage.save(form_data))
        self.save_to_storage()
        return stage.render(request_context)


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
