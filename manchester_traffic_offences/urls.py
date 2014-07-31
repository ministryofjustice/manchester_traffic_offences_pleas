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
                       url(r'^feedback/', include('feedback.urls'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
