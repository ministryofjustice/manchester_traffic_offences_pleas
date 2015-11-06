from .base import *

import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB',''),
        'USER': os.environ.get('POSTGRES_USER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASS', ''),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', ''),
    }
}

ALLOWED_HOSTS = ["api.makeaplea.justice.gov.uk", ]

# Enable CachedStaticFilesStorage for cache-busting assets
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'