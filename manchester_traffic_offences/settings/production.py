from .base import *
import os


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Sym Roe', 'sym.roe@digital.justice.gov.uk'),
    ('Ian George', 'ian.george@digital.justice.gov.uk'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manchester_traffic_offences',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

EMAIL_HOST = os.environ['SENDGRID_EMAIL_HOST']
EMAIL_PORT = os.environ['SENDGRID_EMAIL_PORT']
EMAIL_HOST_USER = os.environ['SENDGRID_EMAIL_HOST_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_EMAIL_HOST_PASSWORD']