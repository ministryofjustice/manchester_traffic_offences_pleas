from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^webhook/$', views.ReceiptWebhook.as_view(), name="receipt_webhook"))