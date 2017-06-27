from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns("",
    url(r"^(?P<stage>.+)/$", views.FeedbackViews.as_view(), name="feedback_form_step"),
    url(r"^$", views.FeedbackViews.as_view(), name="feedback_form"),
)
