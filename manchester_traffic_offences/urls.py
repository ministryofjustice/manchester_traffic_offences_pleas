# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

from django.views.generic import TemplateView

from defendant.views import DefendantLogin
from defendant.decorators import urn_required

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', TemplateView.as_view(template_name="start.html")),
    
    url(r'^urn/', DefendantLogin.as_view(), name="urn"),
    
    url(r'^plea/',
        urn_required(TemplateView.as_view(template_name="plea_form.html")),
        name="plea_form"),
    
    url(r'^feedback/', TemplateView.as_view(
        template_name="feedback.html"), 
        name="feedback"),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
