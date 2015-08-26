from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

from apps.govuk_utils.forms import BaseStageForm, SplitStageForm

from apps.plea.fields import DSRadioFieldRenderer
from apps.plea.forms import to_bool, YESNO_CHOICES

from .fields import ERROR_MESSAGES

SATISFACTION_CHOICES = (
    (5, _("very satisfied")),
    (4, _("satisfied")),
    (3, _("neither satisfied nor dissatisfied")),
    (2, _("dissatisfied")),
    (1, _("very dissatisfied")))


class ServiceForm(SplitStageForm):
    dependencies = {
        "satisfaction": {
            "field": "used_call_centre"
        }
    }

    split_form_options = {
        "trigger": "used_call_centre",
        "nojs_only": True
    }

    used_call_centre = forms.TypedChoiceField(widget=RadioSelect(renderer=DSRadioFieldRenderer),
                                              required=True,
                                              choices=YESNO_CHOICES,
                                              coerce=to_bool,
                                              label=_("Did you use the call centre to help you make your plea?"),
                                              error_messages={"required": ERROR_MESSAGES["USED_CALL_CENTRE_REQUIRED"]})

    satisfaction = forms.ChoiceField(label=_("Overall, how satisfied were you with this service?"),
                                     choices=SATISFACTION_CHOICES,
                                     required=True,
                                     error_messages={"required": ERROR_MESSAGES["SATISFACTION_REQUIRED"]},
                                     widget=RadioSelect(renderer=DSRadioFieldRenderer))

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)

        if self.data.get("used_call_centre") == "True":
            self.fields["satisfaction"].error_messages.update({"required": ERROR_MESSAGES["SATISFACTION_REQUIRED_CALL_CENTRE"]})
        else:
            self.fields["satisfaction"].error_messages.update({"required": ERROR_MESSAGES["SATISFACTION_REQUIRED"]})

class CommentsForm(BaseStageForm):
    comments = forms.CharField(label=_("If you have any further comments about this service, tell us here:"),
                               required=False,
                               widget=forms.Textarea(attrs={"rows": 4,
                                                             "cols": 50,
                                                             "class": "form-control"}))

    email = forms.EmailField(label=_("Email address"),
                             required=False,
                             help_text=_("If you'd like us to get back to you, tell us your email address below:"),
                             widget=forms.TextInput(attrs={"class": "form-control"}))
