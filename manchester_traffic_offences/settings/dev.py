from .base import *
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN', '')
}

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

ADMINS = (
    ('Ian George', 'ian.george@digital.justice.gov.uk'),
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk')
)

MANAGERS = ADMINS
ALLOWED_HOSTS = ["dev.makeaplea.dsd.io", ]

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'email-smtp.eu-west-1.amazonaws.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USERNAME','')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True

# Emails
SMTP_ROUTES["GSI"]["HOST"] = EMAIL_HOST
SMTP_ROUTES["GSI"]["PORT"] = EMAIL_PORT
SMTP_ROUTES["GSI"]["USERNAME"] = EMAIL_HOST_USER
SMTP_ROUTES["GSI"]["PASSWORD"] = EMAIL_HOST_PASSWORD

PLEA_EMAIL_FROM = os.environ.get('PLEA_EMAIL_FROM', '')
PLEA_EMAIL_TO = [os.environ.get('PLEA_EMAIL_TO', '') ]
PLP_EMAIL_TO = [os.environ.get("PLP_EMAIL_TO", '') ]

FEEDBACK_EMAIL_TO = [os.environ.get("FEEDBACK_EMAIL_TO", '')]
FEEDBACK_EMAIL_FROM = os.environ.get("FEEDBACK_EMAIL_FROM", '')
