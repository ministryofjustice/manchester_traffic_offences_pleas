from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import FeedbackForm


def feedback_form(request):
    next = request.GET.get("next", "/")

    if request.method == "POST":
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            return HttpResponseRedirect(next)
        else:
            return render(request, {"form": feedback_form}, "feedback/feedback.html")
    else:
        return render(request, {"form": FeedbackForm()}, "feedback/feedback.html")

