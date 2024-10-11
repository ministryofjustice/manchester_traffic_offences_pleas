from django.urls import re_path as url, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'auditevent', views.AuditEventViewSet)
router.register(r'case', views.CaseViewSet)
router.register(r'result', views.ResultViewSet)
router.register(r'stats', views.PublicStatsViewSet, base_name="stats")


urlpatterns = (
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
