from .base import *
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

RAVEN_CONFIG = {
    'dsn': os.environ['RAVEN_DSN'],
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ.get('POSTGRES_PASS', ''),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', ''),
    }
}


ALLOWED_HOSTS = ["makeaplea.dsd.io", ]
EMAIL_HOST = os.environ['SENDGRID_EMAIL_HOST']
EMAIL_PORT = os.environ['SENDGRID_EMAIL_PORT']
EMAIL_HOST_USER = os.environ['SENDGRID_EMAIL_HOST_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_EMAIL_HOST_PASSWORD']

PLEA_EMAIL_FROM = "makeaplea@digital.justice.gov.uk"
PLEA_EMAIL_TO = ["makeaplea@digital.justice.gov.uk", ]