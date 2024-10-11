from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r"^(?P<stage>.+)/$", views.FeedbackViews.as_view(), name="feedback_form_step"),
    url(r"^$", views.FeedbackViews.as_view(), name="feedback_form"),
]
