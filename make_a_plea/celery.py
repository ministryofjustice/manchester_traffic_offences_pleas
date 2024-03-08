from __future__ import absolute_import

import os
from celery import Celery
from kombu import Queue
import botocore
import boto3
import datetime
from dateutil.tz import tzlocal

from django.conf import settings

if not "DJANGO_SETTINGS_MODULE" in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'make_a_plea.settings.local')

assume_role_cache: dict = {}
def assumed_role_session(role_arn: str, base_session: botocore.session.Session = None):
    base_session = base_session or boto3.session.Session()._session
    fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
        client_creator = base_session.create_client,
        source_credentials = base_session.get_credentials(),
        role_arn = role_arn,
    )
    creds = botocore.credentials.DeferredRefreshableCredentials(
        method = 'assume-role',
        refresh_using = fetcher.fetch_credentials,
        time_fetcher = lambda: datetime.datetime.now(tzlocal())
    )
    botocore_session = botocore.session.Session()
    botocore_session._credentials = creds
    return boto3.Session(botocore_session = botocore_session)

session = assumed_role_session('arn:aws:iam::754256621582:policy/cloud-platform/sqs/cloud-platform-sqs-5f3d35c662e8')
get_sqs_test = session.client('sqs')
print(get_sqs_test)

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
        session: session,
    }
)