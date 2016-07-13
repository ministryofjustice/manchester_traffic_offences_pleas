from django.conf.urls import url, include
from .views import CourtDataView


urlpatterns = (
    url(r"service-status/", CourtDataView.as_view()),
)