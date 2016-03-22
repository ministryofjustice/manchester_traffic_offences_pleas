from __future__ import unicode_literals

from moj_irat.views import PingJsonView

import views

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from apps.plea.views import CourtFinderView

admin.autodiscover()


handler500 = "make_a_plea.views.server_error"

urlpatterns = patterns(
    "",
    url(r"^$", views.start, name="home"),
    url(r"^helping-you-plead-online/$", views.TranslatedView.as_view(template_name="ad_support.html"), name="ad_support"),
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
    url(r"^test-email-attachment/$", views.test_email_attachment, name="test_email_attachment"),
    url(r"^test-resulting-email/$", views.test_resulting_email, name="test_resulting_email"),
    url(r'^ping.json$', PingJsonView.as_view(build_date_key="APP_BUILD_DATE", commit_id_key="APP_GIT_COMMIT"), name='ping_json'),
    url(r'^500.html$', TemplateView.as_view(template_name="500.html"), name='500_page'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
