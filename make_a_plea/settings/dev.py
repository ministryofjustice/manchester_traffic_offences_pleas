import os
import uuid
from .docker import *

DJANGO_DEBUG = True

# aws settings
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'eu-west-2'
AWS_ROLE_ARN = os.getenv('AWS_ROLE_ARN')
# ECR_ROLE_TO_ASSUME_DEV = os.getenv('ECR_ROLE_TO_ASSUME_DEV')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# s3 static settings
AWS_LOCATION = 'static'
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
ALLOWED_HOSTS = ['dev-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk', 'dev-api-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk']

CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", False)
CELERY_BROKER_URL = "SQS://"
REPLY_QUEUE_SUFFIX = os.environ.get("REPLY_QUEUE_SUFFIX")
CELERY_TASK_DEFAULT_QUEUE = "pet-development-celery"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-2',
    'queue_name_prefix': "pet-development-",
    'polling_interval': 1,
    'visibility_timeout': 3600,
    'never_list_queues': True,
    'predefined_queues': {
        'pet-development-celery': {  ## the name of the SQS queue
            'url': 'https://sqs.eu-west-2.amazonaws.com/754256621582/pet-development-celery',
        },
        f'pet-development-{REPLY_QUEUE_SUFFIX}-reply-celery-pidbox': {
            'url': f'https://sqs.eu-west-2.amazonaws.com/754256621582/pet-development-{REPLY_QUEUE_SUFFIX}-reply-celery-pidbox',
        }
    },
    'sts_role_arn': 'arn:aws:iam::754256621582:policy/cloud-platform/sqs/cloud-platform-sqs-5f3d35c662e8'
}