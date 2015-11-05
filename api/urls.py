from django.conf.urls import url, include


urlpatterns = (
    url(r'^v0/', include('api.v0.urls', namespace="api-v0")),
)
