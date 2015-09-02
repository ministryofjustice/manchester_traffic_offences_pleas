from .base import *
import os


DEBUG = False
TEMPLATE_DEBUG = DEBUG

GOOGLE_ANALYTICS_ID = "UA-63449650-1"

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

SMTP_ROUTES["GSI"]["USERNAME"] = os.environ.get("GSI_EMAIL_USERNAME", "")
SMTP_ROUTES["GSI"]["PASSWORD"] = os.environ.get("GSI_EMAIL_PASSWORD", "")
SMTP_ROUTES["PNN"]["USERNAME"] = os.environ.get("PNN_EMAIL_USERNAME", "")
SMTP_ROUTES["PNN"]["PASSWORD"] = os.environ.get("PNN_EMAIL_PASSWORD", "")

RATE_LIMIT = "120/m"

PREMAILER_OPTIONS = {"base_url": "http://makeaplea.dsd.io",
                     "remove_classes": False,
                     "keep_style_tags": True,
                     "cssutils_logging_level": logging.ERROR}

BROKER_TRANSPORT_OPTIONS = {'region': 'eu-west-1',
                            'queue_name_prefix': 'staging-',
                            'polling_interval': 1}

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

ALLOWED_HOSTS = ["staging.makeaplea.dsd.io", "makeaplea.dsd.io"]

# Enable CachedStaticFilesStorage for cache-busting assets
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STORE_USER_DATA = True

ENCRYPTED_COOKIE_KEYS = [
    os.environ["ENCRYPTED_COOKIE_KEY"]
]

