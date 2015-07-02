from django.conf.urls import url, include
from django.views.generic import TemplateView

from .views import HealthCheckView


urlpatterns = (
    url(r"healthcheck$", HealthCheckView.as_view()),
)