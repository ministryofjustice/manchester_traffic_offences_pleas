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


ALLOWED_HOSTS = ["www.makeaplea.justice.gov.uk", ]
EMAIL_HOST = os.environ.get('SENDGRID_EMAIL_HOST', '587')
EMAIL_PORT = os.environ.get('SENDGRID_EMAIL_PORT', 'smtp.sendgrid.net')
EMAIL_HOST_USER = os.environ['SENDGRID_EMAIL_HOST_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_EMAIL_HOST_PASSWORD']

PLEA_EMAIL_FROM = os.environ['PLEA_EMAIL_FROM']
PLEA_EMAIL_TO = [os.environ['PLEA_EMAIL_TO'], ]