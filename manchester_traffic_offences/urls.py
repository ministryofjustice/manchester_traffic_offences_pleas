# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from apps.defendant.views import DefendantLogin
from .views import HomeView

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', HomeView.as_view()),
                       url(r'^urn/', DefendantLogin.as_view(), name="urn"),
                       url(r'^plea/', include('plea.urls', )),
                       url(r'^feedback/', TemplateView.as_view(
                           template_name="feedback.html"),
                           name="feedback"),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
