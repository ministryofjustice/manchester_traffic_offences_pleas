from __future__ import absolute_import

import os
print("Before Celery import")
from celery import Celery
print("After Celery import")

from django.conf import settings

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'make_a_plea.settings.local')

app = Celery('celeryapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

print("Celery app created")