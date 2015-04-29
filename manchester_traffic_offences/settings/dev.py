from .base import *
import os


DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB',''),
        'USER': os.environ.get('POSTGRES_USER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASS', ''),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', ''),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

SMTP_ROUTES["GSI"]["HOST"] = os.environ.get("GSI_EMAIL_HOST", "localhost")
SMTP_ROUTES["GSI"]["PORT"] = os.environ.get("GSI_EMAIL_PORT", 25)
SMTP_ROUTES["GSI"]["USERNAME"] = os.environ.get("GSI_EMAIL_USERNAME", "")
SMTP_ROUTES["GSI"]["PASSWORD"] = os.environ.get("GSI_EMAIL_PASSWORD", "")
SMTP_ROUTES["GMP"]["HOST"] = os.environ.get("GSI_EMAIL_HOST", "localhost")
SMTP_ROUTES["GMP"]["PORT"] = os.environ.get("GSI_EMAIL_PORT", 25)
SMTP_ROUTES["GMP"]["USERNAME"] = os.environ.get("GSI_EMAIL_USERNAME", "")
SMTP_ROUTES["GMP"]["PASSWORD"] = os.environ.get("GSI_EMAIL_PASSWORD", "")

BROKER_TRANSPORT_OPTIONS = {'region': 'eu-west-1',
                            'queue_name_prefix': 'dev-',
                            'polling_interval': 1}

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

ALLOWED_HOSTS = ["dev.makeaplea.dsd.io", ]

# Enable CachedStaticFilesStorage for cache-busting assets
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

TRANSIFEX_USERNAME = os.environ.get("TRANSIFEX_USERNAME", "")
TRANSIFEX_PASSWORD = os.environ.get("TRANSIFEX_PASSWORD", "")
TRANSIFEX_PROJECT_SLUG = os.environ.get("TRANSIFEX_PROJECT_SLUG", "")