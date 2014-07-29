from datetime import datetime

from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from .forms import FeedbackForm


def feedback_form(request):
    nxt = request.GET.get("next", "/")

    if request.method == "POST":
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            email_context = {"question": feedback_form.cleaned_data["question"],
                             "email": feedback_form.cleaned_data["email"],
                             "date_sent": datetime.now()}

            email = EmailMessage("Feedback from makeaplea.justice.gov.uk",
                                 render_to_string("feedback/feedback_email.html",
                                                  email_context),
                                 "ian.george@digital.justice.gov.uk",
                                 ("ian.george@digital.justice.gov.uk", ))
            email.content_subtype = "html"
            email.send()
            messages.add_message(request, messages.INFO, "Thanks for your feedback.")
            return HttpResponseRedirect(nxt)
        else:
            return render(request, "feedback/feedback.html", {"form": feedback_form})
    else:
        return render(request, "feedback/feedback.html", {"form": FeedbackForm()})

