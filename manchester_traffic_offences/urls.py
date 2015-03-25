# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

from apps.plea.views import CourtFinderView

import views

handler500 = "manchester_traffic_offences.views.server_error"

urlpatterns = patterns('',
    url(r'^$', views.HomeView.as_view(), name="home"),
    url(r'^terms-and-conditions-and-privacy-policy$',
       TemplateView.as_view(template_name="terms.html"),
       name="terms"),
    url(r'^plea/', include('apps.plea.urls', )),
    url(r'^feedback/', include('apps.feedback.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^court-finder/$', CourtFinderView.as_view()),
    url(r'^i18n/', include('django.conf.urls.i18n')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
