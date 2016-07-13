from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from .views import CourtDataView


urlpatterns = (
    url(r"service-status/", staff_member_required(CourtDataView.as_view())),
)