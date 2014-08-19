from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from .forms import FeedbackForm


def feedback_form(request):
    kw_args = {k: v for (k, v) in request.GET.items()}
    nxt = kw_args.pop("next", "/")
    try:
        if kw_args:
            nxt_url = reverse(nxt, kwargs=kw_args)
        else:
            nxt_url = reverse(nxt)
    except NoReverseMatch:
        nxt_url = reverse("home")
    if request.method == "POST":
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            email_context = {"question": feedback_form.cleaned_data["feedback_question"],
                             "email": feedback_form.cleaned_data["feedback_email"],
                             "date_sent": datetime.now(),
                             "referrer": nxt_url,
                             "user_agent": request.META["HTTP_USER_AGENT"]}

            email = EmailMessage("Feedback from makeaplea.justice.gov.uk",
                                 render_to_string("feedback/email.html",
                                                  email_context),
                                 settings.FEEDBACK_EMAIL_FROM,
                                 settings.FEEDBACK_EMAIL_TO)
            email.content_subtype = "html"
            email.send(fail_silently=False)
            messages.add_message(request, messages.INFO, "Thanks for your feedback.")
            return HttpResponseRedirect(nxt_url)
        else:
            return render(request, "feedback/feedback.html", {"form": feedback_form})
    else:
        return render(request, "feedback/feedback.html", {"form": FeedbackForm()})

