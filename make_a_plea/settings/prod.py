from .docker import *
import os

# aws settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME_PROD')
ECR_ROLE_TO_ASSUME_PROD = os.getenv('ECR_ROLE_TO_ASSUME_PROD')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# s3 static settings
AWS_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
ALLOWED_HOSTS = ['prod-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk']

CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", False)
CELERY_BROKER_URL = "SQS://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-2',
    'queue_name_prefix': "pet-production-",
    'polling_interval': 1,
    'visibility_timeout': 3600
}