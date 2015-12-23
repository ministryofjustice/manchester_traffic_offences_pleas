from .base import *
from make_a_plea.settings.testing import GPG_TEST_KEY

ADMINS = (
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB','manchester_traffic_offences'),
        'USER': os.environ.get('POSTGRES_USER', 'jenkins'),
        'PASSWORD': os.environ.get('POSTGRES_PASS', 'moomoo'),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', ''),
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

