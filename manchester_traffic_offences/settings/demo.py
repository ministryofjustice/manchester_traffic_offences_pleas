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

ADMINS = (
    ('Sym Roe', 'sym.roe@digital.justice.gov.uk'),
    ('Ian George', 'ian.george@digital.justice.gov.uk'),
)

MANAGERS = ADMINS


ALLOWED_HOSTS = ["makeaplea.dsd.io", ]
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'email-smtp.eu-west-1.amazonaws.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True

PLEA_EMAIL_FROM = os.environ['PLEA_EMAIL_FROM']
PLEA_EMAIL_TO = [os.environ['PLEA_EMAIL_TO'], ]
PLP_EMAIL_TO = [os.environ["PLP_EMAIL_TO"], ]
