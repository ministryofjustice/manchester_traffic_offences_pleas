from __future__ import absolute_import

import os
from celery import Celery
from kombu import Queue

from django.conf import settings

if not "DJANGO_SETTINGS_MODULE" in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'make_a_plea.settings.local')

app = Celery('apps.plea')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    broker_url = 'sqs://',
    task_queues = [
        Queue('pet-development-celery')
    ],
    task_create_missing_queues = False,
    task_default_queue = 'pet-development-celery',
    broker_transport_options={
        'region': 'eu-west-2',
        'predefined_queues': {
            'pet-development-celery': {  ## the name of the SQS queue
                'url': 'https://sqs.eu-west-2.amazonaws.com/754256621582/pet-development-celery',
            }
        },
        'sts_role_arn': 'arn:aws:iam::754256621582:policy/cloud-platform/sqs/cloud-platform-sqs-5f3d35c662e8'
    }
)