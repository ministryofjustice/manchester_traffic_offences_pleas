from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<stage>.+)/$', views.PleaOnlineViews.as_view(), name='plea_form_step'),
    url(r'^$', views.PleaOnlineViews.as_view(), name='plea_form')
)