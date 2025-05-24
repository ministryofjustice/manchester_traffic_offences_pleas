from .base import *
import os


DEBUG = os.environ.get("DJANGO_DEBUG", "") == "True"
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', ''),
        'USER': os.environ.get('DB_USERNAME', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

SMTP_ROUTES["GSI"]["USERNAME"] = os.environ.get("GSI_EMAIL_USERNAME", "")
SMTP_ROUTES["GSI"]["PASSWORD"] = os.environ.get("GSI_EMAIL_PASSWORD", "")
SMTP_ROUTES["PNN"]["USERNAME"] = os.environ.get("PNN_EMAIL_USERNAME", "")
SMTP_ROUTES["PNN"]["PASSWORD"] = os.environ.get("PNN_EMAIL_PASSWORD", "")

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "localhost:8000"), ]

# Enable CachedStaticFilesStorage for cache-busting assets
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", False)
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "SQS://")
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-1',
    'queue_name_prefix': os.environ.get("CELERY_QUEUE_POLLING_PREFIX", "dev-"),
    'polling_interval': 1,
    'visibility_timeout': 3600
}


#
# Temporary keys to run collectstatic on docker image build.
#
# Override in your environment.
#
SECRET_KEY = os.environ.get("SECRET_KEY", "*** REMOVED ***")

STORE_USER_DATA = False
