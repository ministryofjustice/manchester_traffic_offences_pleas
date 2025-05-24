import os

from .base import *

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

logging.disable(logging.CRITICAL)

ADMINS = (
    ('[DEV] HMCTS Reform Sustaining Support', 'sustainingteamdev@hmcts.net'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'manchester_traffic_offences'),
        'USER': os.environ.get('POSTGRES_USER', 'jenkins'),
        'PASSWORD': os.environ.get('POSTGRES_PASS', 'moomoo'),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', ''),
    }
}

CELERY_BROKER_URL = "amqp://localhost"

EMAIL_PORT = 1025
EMAIL_HOST = "127.0.0.1"
EMAIL_USE_TLS = False

SMTP_ROUTES = {"GSI": {"HOST": "127.0.0.1", "PORT": 1025, "USE_TLS": False},
               "PNN": {"HOST": "127.0.0.1", "PORT": 1025, "USE_TLS": False},
               "PUB": {"HOST": "127.0.0.1", "PORT": 1025, "USE_TLS": False}}
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECRET_KEY = "fjsklfosufcilsft37dGDRR%^$%^^gfsdvf"

# the test user data directory
USER_DATA_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_user_data')
GPG_HOME_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_gpg_home')
GPG_RECIPIENT = "test@example.org"

TEST_RUNNER = 'make_a_plea.runner.MAPTestRunner'


# a test gpg key with no passphrase and email test@example.org

GPG_TEST_KEY = ""

