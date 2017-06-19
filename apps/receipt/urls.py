from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^webhook/$', views.ReceiptWebhook.as_view(), name="receipt_webhook")
]
