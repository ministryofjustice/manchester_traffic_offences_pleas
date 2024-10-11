from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^webhook/$', views.ReceiptWebhook.as_view(), name="receipt_webhook")
]
