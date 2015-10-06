import sys
import os
from os.path import join, abspath, dirname
import logging

from django.utils.translation import ugettext_lazy as _

VERSION = (0, 9, 5)

# PATH vars
here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

DEBUG = True
template_DEBUG = DEBUG

ADMINS = (
    ('Ian George', 'ian.george@digital.justice.gov.uk'),
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk')
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manchester_traffic_offences',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

RAVEN_CONFIG = {
    'dsn': os.environ.get("RAVEN_DSN", ""),
}



# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

LANGUAGES = (
    ('en', _('English')),
    ('cy', _('Welsh')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True 

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Allow the use of commas in decimal fields and when displaying large numbers
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = u','

LOCALE_PATHS = (
    root('../conf/locale'),
)

# Force admin language
ADMIN_LANGUAGE_CODE = "en"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = root('assets', 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = root('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    root('assets'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Options for Premailer, which inlines the CSS on the fly in email templates and
# makes all URLs absolute
PREMAILER_OPTIONS = {"base_url": "https://www.makeaplea.justice.gov.uk",
                     "remove_classes": False,
                     "keep_style_tags": True,
                     "cssutils_logging_level": logging.ERROR}

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY", "")

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.plea.middleware.TimeoutRedirectMiddleware',
    'make_a_plea.middleware.AdminLocaleURLMiddleware',
)

ROOT_URLCONF = 'make_a_plea.urls'

SESSION_SERIALIZER = 'make_a_plea.serializers.DateAwareSerializer'
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600

CSRF_COOKIE_HTTPONLY = True

RATE_LIMIT = "20/m"

WAFFLE_CACHE_PREFIX = "MaP_waffle"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'make_a_plea.wsgi.application'

TEMPLATE_DIRS = (
    "templates",
    root('templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    'django.core.context_processors.request',
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.contrib.auth.context_processors.auth",
    "make_a_plea.context_processors.globals",
    "apps.feedback.context_processors.feedback",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'djcelery',
    'waffle',
    'moj_template',
    'apps.forms',
    'apps.plea',
    'apps.feedback',
    'apps.receipt',
    'django_premailer',
]

INSTALLED_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps.plea.email': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
        },
        'apps.plea.tasks': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
        }
    }
}

INTERNAL_IPS = ['127.0.0.1']

# EMAILS
BROKER_URL = "SQS://"
BROKER_TRANSPORT_OPTIONS = {'region': 'eu-west-1'}
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'

SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "")

# Secure mail
SMTP_ROUTES = {"GSI": {"HOST": os.environ.get("GSI_EMAIL_HOST", "localhost"),
                       "PORT": os.environ.get("GSI_EMAIL_PORT", 25)},
               "PNN": {"HOST": os.environ.get("PNN_EMAIL_HOST", "localhost"),
                       "PORT": os.environ.get("PNN_EMAIL_PORT", 25),}}

# Public email
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 25)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 60

# Full plea email sent to court mailbox
PLEA_EMAIL_FROM = os.environ.get("PLEA_EMAIL_FROM", "plea_from@example.org")
PLEA_EMAIL_SUBJECT = u"ONLINE PLEA: {case[urn]} DOH: {email_date_of_hearing} {email_name}"
PLEA_EMAIL_BODY = ""
PLEA_EMAIL_ATTACHMENT_NAME = "plea.html"

# Cut down email sent to the police prosecutor
PLP_EMAIL_FROM = os.environ.get("PLP_EMAIL_FROM", "plea_from@example.org")
PLP_EMAIL_SUBJECT = u"POLICE {0}".format(PLEA_EMAIL_SUBJECT)

# Feedback email
FEEDBACK_EMAIL_FROM = os.environ.get("FEEDBACK_EMAIL_FROM", "plea_feedback@example.org")
FEEDBACK_EMAIL_TO = (os.environ.get("FEEDBACK_EMAIL_TO", "plea_feedback_to@example.org"), )

# Emails to users
PLEA_CONFIRMATION_EMAIL_FROM = os.environ.get("PLEA_CONFIRMATION_EMAIL_FROM", "")
PLEA_CONFIRMATION_EMAIL_BCC = []
SEND_PLEA_CONFIRMATION_EMAIL = True


RECEIPT_INBOX_FROM_EMAIL = os.environ.get("RECEIPT_INBOX_FROM_EMAIL", "")
RECEIPT_INBOX_USERNAME = os.environ.get("RECEIPT_INBOX_USERNAME", "")
RECEIPT_INBOX_PASSWORD = os.environ.get('RECEIPT_GMAIL_PASSWORD', '')
RECEIPT_INBOX_OAUTH_API_KEY = ""
RECEIPT_ADMIN_EMAIL_ENABLED = True
RECEIPT_ADMIN_EMAIL_SUBJECT = "Makeaplea receipt processing script"
RECEIPT_HEADER_FRAGMENT_CHECK = os.environ.get("RECEIPT_HEADER_FRAGMENT_CHECK", "")

USER_DATA_DIRECTORY = os.environ.get('USER_DATA_DIRECTORY', os.path.abspath(here('../../user_data')))
GPG_RECIPIENT = os.environ.get('GPG_RECIPIENT', 'test@test.com')
GPG_HOME_DIRECTORY = os.environ.get('GPG_HOME_DIRECTORY', '/home/vagrant/.gnupg/')

ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "")
FTP_SERVER_IP = os.environ.get("FTP_SERVER_IP", "")

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass
