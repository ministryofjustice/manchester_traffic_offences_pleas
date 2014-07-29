# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from .views import HomeView

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', HomeView.as_view()),
                       url(r'^plea/', include('plea.urls', )),
                       url(r'^feedback/', include('feedback.urls'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
