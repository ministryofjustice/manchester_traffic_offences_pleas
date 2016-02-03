from .base import *
import os


DEBUG = False
TEMPLATE_DEBUG = DEBUG

GOOGLE_ANALYTICS_ID = "UA-53811587-1"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ.get('POSTGRES_PASS', ''),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', ''),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

BROKER_TRANSPORT_OPTIONS = {'region': 'eu-west-1',
                            'queue_name_prefix': 'production-',
                            'polling_interval': 1,
                            'visibility_timeout': 3600}

ALLOWED_HOSTS = ["www.makeaplea.justice.gov.uk", "www.makeaplea.service.gov.uk"]

# Enable CachedStaticFilesStorage for cache-busting assets
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STORE_USER_DATA = True

ENCRYPTED_COOKIE_KEYS = [
    os.environ["ENCRYPTED_COOKIE_KEY"]
]

REDIRECT_START_PAGE = "https://www.gov.uk/make-a-plea"

RATE_LIMIT = "500/m"
