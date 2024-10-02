from .docker import *
import os

DJANGO_DEBUG = False

AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME_PREPROD')
AWS_S3_REGION_NAME = 'eu-west-2'
AWS_ROLE_ARN = os.getenv('AWS_ROLE_ARN')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_LOCATION = 'static'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
ALLOWED_HOSTS = ['preprod-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk', 'preprod-api-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk']
CELERY_BROKER_URL = "SQS://"
CELERY_TASK_DEFAULT_QUEUE = "pet-preprod-celery"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-2',
    'predefined_queues': {
        'pet-preprod-celery': {  ## the name of the SQS queue
            'url': 'https://sqs.eu-west-2.amazonaws.com/754256621582/pet-preprod-celery',
        }
    }
}
USER_DATA_DIRECTORY = "/user_data"