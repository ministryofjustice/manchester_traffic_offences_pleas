from __future__ import absolute_import

import os
from celery import Celery

from django.conf import settings

if not "DJANGO_SETTINGS_MODULE" in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'make_a_plea.settings.local')

app = Celery('apps.plea')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
