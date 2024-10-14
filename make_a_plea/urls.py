from __future__ import unicode_literals

from moj_irat.views import PingJsonView, HealthcheckView

from . import views
from django.conf import settings
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from apps.plea.views import CourtFinderView

admin.autodiscover()

handler500 = "make_a_plea.views.server_error"

urlpatterns = [
    path("", views.start, name="home"),
    path("helping-you-plead-online/", views.TranslatedView.as_view(template_name="ad_support.html"), name="ad_support"),
    path("terms-and-conditions-and-privacy-policy/", views.TranslatedView.as_view(template_name="terms.html"), name="terms"),
    path("plea/", include("apps.plea.urls")),
    path("receipt/", include("apps.receipt.urls")),
    path("feedback/", include("apps.feedback.urls")),
    path("reports/", include("apps.reports.urls", namespace='reports')),
    path("admin/", admin.site.urls),
    path("nested_admin/", include('nested_admin.urls')),
    path("court-finder/", CourtFinderView.as_view(), name="court_finder"),
    path("change-language/", views.set_language, name="set_language"),
    path("set-a11y-testing/", views.set_a11y_testing, name="set_a11y_testing"),
    path("session-timeout/", TemplateView.as_view(template_name="session_timeout.html"), name="session_timeout"),
    path("", include("apps.monitoring.urls")),
    path("test-template/", views.test_template, name="test_template"),
    path("test-email-attachment/", views.test_email_attachment, name="test_email_attachment"),
    path("test-resulting-email/", views.test_resulting_email, name="test_resulting_email"),
    path("healthcheck", HealthcheckView.as_view(), name='healthcheck'),
    path("ping.json", PingJsonView.as_view(
        build_date_key="APP_BUILD_DATE",
        commit_id_key="APP_GIT_COMMIT",
        build_tag_key="APP_BUILD_TAG"
    ), name='ping_json'),
    path("500.html", TemplateView.as_view(template_name="500.html"), name='500_page'),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.ico', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)