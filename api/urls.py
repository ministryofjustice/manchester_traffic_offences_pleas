from django.urls import re_path as url, include


urlpatterns = (
    url(r'^v0/', include('api.v0.urls', namespace="api-v0")),
)
