from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from apps.forms.stages import FormStage

from .forms import ServiceForm, CommentsForm
from .models import UserRating
from .email import send_feedback_email


class ServiceStage(FormStage):
    name = "service"
    template = "service.html"
    form_class = ServiceForm
    dependencies = []


class CommentsStage(FormStage):
    name = "comments"
    template = "comments.html"
    form_class = CommentsForm
    dependencies = ["service"]

    def save(self, form_data, next_step=None):
        clean_data = super(CommentsStage, self).save(form_data, next_step)

        if clean_data.get("complete", False):
            email_data = {k: v for k, v in self.all_data.items()}
            email_data.update({"comments": clean_data})
            email_result = send_feedback_email(email_data)
            if email_result:
                self.add_message(messages.SUCCESS, _("Your feedback has been submitted"))
                UserRating.objects.record(self.all_data["service"]["service_satisfaction"], self.all_data["service"]["call_centre_satisfaction"])
                self.set_next_step("complete")
            else:
                self.add_message(messages.ERROR, '<h2 class="heading-medium">{}</h2><p>{}</p>'.format(
                    _("Submission Error"),
                    _("There seems to have been a problem submitting your feedback. Please try again.")))
                self.set_next_step("comments")

        return clean_data


class CompleteStage(FormStage):
    name = "complete"
    template = None
    form_class = None
    dependencies = ["service", "comments"]
