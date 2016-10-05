from django.conf.urls import url
from django.views.decorators.cache import cache_page

from .views import CourtDataView


urlpatterns = (
    url(r"service-status/", cache_page(60*60*24)(CourtDataView.as_view())),
)