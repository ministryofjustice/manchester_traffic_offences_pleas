from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^urn_used/$', views.UrnAlreadyUsedView.as_view(), name='urn_already_used'),
    url(r'^(?P<stage>.+)/(?P<index>.+)$', views.PleaOnlineViews.as_view(), name='plea_form_step'),
    url(r'^(?P<stage>.+)/$', views.PleaOnlineViews.as_view(), name='plea_form_step'),
    url(r'^$', views.PleaOnlineViews.as_view(), name='plea_form'),
)