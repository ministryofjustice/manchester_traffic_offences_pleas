import datetime

from django import forms
from django.forms.widgets import MultiWidget, RadioSelect
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class DSRadioSelect(RadioSelect):
    template_name = "widgets/partials/DSRadioSelect.html"

    def render(self, name, value, attrs=None, *args, **kwargs):
        """
        Outputs a GOV.UK-styled <fieldset> for this set of choice fields.
        Radio buttons line up alongside each other.
        """
        context = {
            "id": self.attrs.get('id', None),
            "self": self,
            "name": name,
            "value": value,
        }
        return render_to_string(self.template_name, context)


class DSStackedRadioSelect(DSRadioSelect):
    template_name = "widgets/partials/DSStackedRadioSelect.html"


class DSTemplateWidgetBase(forms.TextInput):
    template = ""

    def __init__(self, attrs=None, context=None):
        label = attrs.pop("title", None)

        super(DSTemplateWidgetBase, self).__init__(attrs)

        try:
            self.context = context.update({"label": label})
        except AttributeError:
            self.context = {"label": label}

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        rendered_widget = super(DSTemplateWidgetBase, self).render(name, value, attrs)
        context = {"name": name, "value": value, "attrs": final_attrs, "field": rendered_widget}
        context.update(**self.context)
        return render_to_string(self.template, context)


class DSDateTemplateWidget(DSTemplateWidgetBase):
    template = "widgets/partials/DSDateInputWidget.html"


class DateWidget(MultiWidget):
    def __init__(self, attrs=None):

        widgets = [DSDateTemplateWidget(attrs={"pattern": "[0-9]*",
                                               "maxlength": "2",
                                               "size": "2",
                                               "class": "form-control-day",
                                               "title": _("Day")}),
                   DSDateTemplateWidget(attrs={"pattern": "[0-9]*",
                                               "maxlength": "2",
                                               "size": "2",
                                               "class": "form-control-month",
                                               "title": _("Month")}),
                   DSDateTemplateWidget(attrs={"pattern": "[0-9]*",
                                               "maxlength": "4",
                                               "size": "4",
                                               "class": "form-control-year",
                                               "title": _("Year")}),
                   ]
        super(DateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if not value:
            return ["", "", ""]
        elif isinstance(value, datetime.date):
            return [value.day, value.month, value.year]
        else:
            year, month, day = value.split("-")
            return [day, month, year]

    def value_from_datadict(self, data, files, name):
        day, month, year = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)
        ]

        try:
            day = int(day)
        except (ValueError, TypeError):
            day = None

        try:
            month = int(month)
        except (ValueError, TypeError):
            try:
                month = datetime.datetime.strptime(month, "%b").month
            except (ValueError, TypeError):
                try:
                    month = datetime.datetime.strptime(month, "%B").month
                except (ValueError, TypeError):
                    month = None

        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None

        if day == month == year is None:
            return ""

        try:
            return str(datetime.date(day=day, month=month, year=year))
        except (ValueError, TypeError):
            return [widget.value_from_datadict(data, files, name + "_%s" % i) for i, widget in enumerate(self.widgets)]

    def format_output(self, rendered_widgets):
        return " / ".join(rendered_widgets)
