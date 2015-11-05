from .base import *
from make_a_plea.settings.testing import GPG_TEST_KEY

ADMINS = (
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manchester_traffic_offences',
        'USER': 'jenkins',
        'PASSWORD': 'moomoo',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

DEBUG = False

SECRET_KEY = "Trdfgjgfghfdgjlfdtr_+@3gvuedrs873w"

# the test user data directory
USER_DATA_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_user_data')
GPG_HOME_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_gpg_home')
GPG_RECIPIENT = "test@test.com"

TEST_RUNNER = 'make_a_plea.runner.MAPTestRunner'

ENCRYPTED_COOKIE_KEYS = [
    '9evXbsR_1yZA5EW_blSI4O69MjGKwOu1-UwLK_PWyKw=',
]

