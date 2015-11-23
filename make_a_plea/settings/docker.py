from .base import *
import os


DEBUG = True 
TEMPLATE_DEBUG = DEBUG

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

ALLOWED_HOSTS = ["localhost:8000", ]

# Enable CachedStaticFilesStorage for cache-busting assets
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CELERY_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", True)

ENCRYPTED_COOKIE_KEYS = [
    os.environ["ENCRYPTED_COOKIE_KEY"]
]
