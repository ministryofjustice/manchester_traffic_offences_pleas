from django.conf.urls import patterns, url
from django.contrib.auth import views as django_views
from django.core.urlresolvers import reverse_lazy

from . import views

urlpatterns = patterns('',
    url(r'^example/$', views.ExampleStep.as_view(), name='example_step'),
    url(r'^review/$', views.ReviewStep.as_view(), name='review_step'),
)