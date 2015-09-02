from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _

YESNO_CHOICES_1 = (
    (True, _("Yes (v1)")),
    (False, _("No (v1)"))
)

YESNO_CHOICES_2 = (
    (True, _("Yes (v2)")),
    (False, _("No (v2)"))
)

YESNO_CHOICES_3 = (
    (True, _("Yes (v3)")),
    (False, _("No (v3)"))
)

YESNO_CHOICES_4 = (
    (True, _("Yes (v4)")),
    (False, _("No (v4)"))
)

to_bool = lambda x: x == "True"

class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class BaseStageForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseStageForm, self).__init__(*args, **kwargs)
        try:
            self.data = args[0]
        except IndexError:
            self.data = kwargs.get("data", {})

        self.split_form = self.data.get("split_form", None)

        if hasattr(self, "dependencies"):
            prefix = kwargs.get("prefix", None)
            self.check_dependencies(self.dependencies, prefix)

    def check_dependencies(self, dependencies_list, prefix=None):
        """
        Set the required attribute depending on the dependencies map
        and the already submitted data
        """
        for field, dependency in dependencies_list.items():
            dependency_field = dependency.get("field", None)
            dependency_value = dependency.get("value", None)
            sub_dependencies = dependency.get("dependencies", None)

            """
            When a form has a prefix, the key in the field is the original,
            but the key in data is updated. Would there be a nicer way of
            handling this?
            """
            if prefix:
                dependency_field_data_key = prefix + "-" + dependency_field
            else:
                dependency_field_data_key = dependency_field

            if self.fields.get(field, None):

                self.fields[field].required = False

                if self.fields[dependency_field].required:
                    if self.split_form is None or self.split_form != dependency_field:
                        if dependency_value and self.data.get(dependency_field_data_key, None) == dependency_value:
                            self.fields[field].required = True
                        
                        if not dependency_value and self.data.get(dependency_field_data_key, None) is not None:
                            self.fields[field].required = True

                    if sub_dependencies:
                        self.check_dependencies(sub_dependencies, prefix)


class SplitStageForm(BaseStageForm):
    split_form = forms.CharField(widget=forms.HiddenInput(), required=False)

    split_form_options = {}

    def __init__(self, *args, **kwargs):
        super(SplitStageForm, self).__init__(*args, **kwargs)

        if self.split_form is None:
            self.fields["split_form"].initial = self.split_form_options.get("trigger", False)

        if self.split_form_options.get("nojs_only", False):
            self.fields["split_form"].widget.attrs.update({"class": "nojs-only"})
