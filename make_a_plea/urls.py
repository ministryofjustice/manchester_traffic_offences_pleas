from __future__ import unicode_literals

from moj_irat.views import PingJsonView, HealthcheckView

from . import views
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from apps.plea.views import CourtFinderView

admin.autodiscover()


handler500 = "make_a_plea.views.server_error"

urlpatterns = [
    url(r"^$", views.start, name="home"),
    url(r"^helping-you-plead-online/$", views.TranslatedView.as_view(template_name="ad_support.html"), name="ad_support"),
    url(r"^terms-and-conditions-and-privacy-policy/$", views.TranslatedView.as_view(template_name="terms.html"), name="terms"),
    url(r"^plea/", include("apps.plea.urls", )),
    url(r"^receipt/", include("apps.receipt.urls")),
    url(r"^feedback/", include("apps.feedback.urls")),
    url(r"^reports/", include("apps.reports.urls", namespace='reports')),
    url(r"^admin/", include(admin.site.urls)),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r"^court-finder/$", CourtFinderView.as_view(), name="court_finder"),
    url(r"^change-language/$", views.set_language, name="set_language"),
    url(r"^set-a11y-testing/$", views.set_a11y_testing, name="set_a11y_testing"),
    url(r"^session-timeout/$", TemplateView.as_view(template_name="session_timeout.html"), name="session_timeout"),
    url(r"^", include("apps.monitoring.urls")),
    url(r"^test-template/$", views.test_template, name="test_template"),
    url(r"^test-email-attachment/$", views.test_email_attachment, name="test_email_attachment"),
    url(r"^test-resulting-email/$", views.test_resulting_email, name="test_resulting_email"),
    url(r'^healthcheck$', HealthcheckView.as_view(), name='healthcheck'),
    url(r'^ping.json$', PingJsonView.as_view(
        build_date_key="APP_BUILD_DATE",
        commit_id_key="APP_GIT_COMMIT",
        build_tag_key="APP_BUILD_TAG"
    ), name='ping_json'),
    url(r'^500.html$', TemplateView.as_view(template_name="500.html"), name='500_page'),
    url(r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.ico', permanent=True)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
