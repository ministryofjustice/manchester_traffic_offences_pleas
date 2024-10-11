from django.urls import re_path as url

from .views import CourtDataView


urlpatterns = (
    url(r"service-status/", CourtDataView.as_view()),
)
