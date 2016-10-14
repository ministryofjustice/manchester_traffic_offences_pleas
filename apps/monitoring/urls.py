from django.conf.urls import url

from .views import CourtDataView


urlpatterns = (
    url(r"service-status/", CourtDataView.as_view()),
)
