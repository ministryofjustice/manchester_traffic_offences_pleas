from django.conf import settings
from django.conf.urls import include, url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^index$', views.index, name='index'),
    url(r'^plea_report', views.plea_report, name='plea_report'),
    url(r'^$', views.index, name='index')
]