from django.conf.urls import patterns, url

from .views import feedback_form

urlpatterns = patterns('',
                       url(r'^$', feedback_form, name="feedback_form"))