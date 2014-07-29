# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

import views

admin.autodiscover()

handler500 = "manchester_traffic_offences.views.server_error"

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', views.HomeView.as_view()),
                       url(r'^plea/', include('plea.urls', )),
                       # temporary url for testing the 500 page, should be removed before launch
                       url(r'^500/', views.server_error),
                       url(r'^feedback/', TemplateView.as_view(
                           template_name="feedback.html"),
                           name="feedback"),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
