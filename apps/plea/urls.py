from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^stats/$', views.stats, name='stats'),
    url(r'^urn_used/$', views.UrnAlreadyUsedView.as_view(), name='urn_already_used'),
    url(r'^(?P<stage>.+)/(?P<index>.+)$', views.PleaOnlineViews.as_view(), name='plea_form_step'),
    url(r'^(?P<stage>.+)/$', views.PleaOnlineViews.as_view(), name='plea_form_step'),
    url(r'^$', views.PleaOnlineViews.as_view(), name='plea_form'),
]
