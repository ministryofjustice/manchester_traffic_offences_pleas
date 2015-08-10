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

urlpatterns = patterns("",
    url(r"^$", views.HomeView.as_view(), name="home"),
    url(r"^terms-and-conditions-and-privacy-policy/$", views.TranslatedView.as_view(template_name="terms.html"), name="terms"),
    url(r"^plea/", include("apps.plea.urls", )),
    url(r"^receipt/", include("apps.receipt.urls")),
    url(r"^feedback/", include("apps.feedback.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^court-finder/$", CourtFinderView.as_view(), name="court_finder"),
    url(r"^change-language/$", views.set_language, name="set_language"),
    url(r"^set-a11y-testing/$", views.set_a11y_testing, name="set_a11y_testing"),
    url(r"^session-timeout/$", TemplateView.as_view(template_name="session_timeout.html"), name="session_timeout"),
    url(r"^", include("apps.monitoring.urls")),
    url(r"^test-template/$", views.test_template, name="test_template"),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
