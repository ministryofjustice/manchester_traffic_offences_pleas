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

PREMAILER_OPTIONS = {"base_url": "http://dev.makeaplea.dsd.io",
                     "remove_classes": False,
                     "keep_style_tags": True,
                     "cssutils_logging_level": logging.ERROR}

SMTP_ROUTES["GSI"]["USERNAME"] = os.environ.get("GSI_EMAIL_USERNAME", "")
SMTP_ROUTES["GSI"]["PASSWORD"] = os.environ.get("GSI_EMAIL_PASSWORD", "")
SMTP_ROUTES["PNN"]["USERNAME"] = os.environ.get("PNN_EMAIL_USERNAME", "")
SMTP_ROUTES["PNN"]["PASSWORD"] = os.environ.get("PNN_EMAIL_PASSWORD", "")

BROKER_TRANSPORT_OPTIONS = {'region': 'eu-west-1',
                            'queue_name_prefix': 'dev-',
                            'polling_interval': 1,
                            'visibility_timeout': 3600}

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

ALLOWED_HOSTS = ["dev.makeaplea.dsd.io", ]

# Enable CachedStaticFilesStorage for cache-busting assets
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ENCRYPTED_COOKIE_KEYS = [
    os.environ["ENCRYPTED_COOKIE_KEY"]
]
