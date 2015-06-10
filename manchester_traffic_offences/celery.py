from __future__ import absolute_import

import os
from celery import Celery

from django.conf import settings

if not os.environ.has_key("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manchester_traffic_offences.settings.local')

app = Celery('apps.plea')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)