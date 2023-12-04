from .docker import *

DJANGO_DEBUG = False

# aws settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
ECR_ROLE_TO_ASSUME_DEV = os.getenv('ECR_ROLE_TO_ASSUME_DEV')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# s3 static settings
AWS_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
ALLOWED_HOSTS = ['dev-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk']
GOV_NOTIFY_API = os.getenv('GOV_NOTIFY_API')

CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", False)
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "SQS://")
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-2',
    'queue_name_prefix': os.environ.get("CELERY_QUEUE_POLLING_PREFIX", "pet-development-"),
    'polling_interval': 1,
    'visibility_timeout': 3600
}