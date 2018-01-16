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
               "PNN": {"HOST": "127.0.0.1", "PORT": 1025, "USE_TLS": False}}
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECRET_KEY = "fjsklfosufcilsft37dGDRR%^$%^^gfsdvf"

# the test user data directory
USER_DATA_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_user_data')
GPG_HOME_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_gpg_home')
GPG_RECIPIENT = "test@example.org"

TEST_RUNNER = 'make_a_plea.runner.MAPTestRunner'


# a test gpg key with no passphrase and email test@example.org

GPG_TEST_KEY = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1

mI0EVopyzQEEANX1gumVEgl1n7puUWcWU3bNvhceeqTLVDhV+YL8/yVSp2iJjPvZ
01N0Or5tVsVhQ0wcnfsD8ChGQx+RFiNjKLKiT059RVxO//6Fr/TeHSRx0CcfQjSB
agbCi9eRt1JbM4BXCO8Gl6zd3kMK9B7rnmvMGNHfezjmWayJA+kxqaeFABEBAAG0
HFRlc3QgVXNlciA8dGVzdEBleGFtcGxlLm9yZz6IuAQTAQIAIgUCVopyzQIbAwYL
CQgHAwIGFQgCCQoLBBYCAwECHgECF4AACgkQkqQuYDyT6m4XEAQAoCxG3ExG07FF
Rh/V1j8+erbI9UzvYnmVWBnqoRbLk8Y6+IdNnmcdWC5ikUcEBNTdU2Nb/J6TOL3B
INTwlZ+0JVJJSMU6uG18D/je2peWWa9sVnhVIZDEGwmdq29dxdD6eS4/O+SQx3oY
x+BuTJiqTqsBRvZB2eVFSyUvGqUU/Yy4jQRWinLNAQQAwA+t/c4tXLXjX8NMKRmQ
Pa3DP2hZbjfNSimzQjhwjE8r5EWj7962M+JSiXpSl+fK9Hvyjif282/+R/SJc2QC
qbeNfHKFPjjJS7PU1QikuNHKuFv3sw/+0vm0NXsuuRZkOkfseqdSvgmdoo3Q7eBw
+HD3xZbDjA6pMqRWZ9Et0KMAEQEAAYieBBgBAgAJBQJWinLNAhsMAAoJEJKkLmA8
k+puxzMD+Je2Y5Q4132TNFgU1GyNxuuRqFYnu85tLVXSRC+zc8ozsh0226hN2e6D
E5ptte+HPWHDdA/AmKmg+SHwJyKWdRsYo2wTADjcXx5wi+0m64MWcFFb1epCYDKZ
OlryOtrddeZ3X65no3P/wMtxicBZuFZ4/XDrpQCOygYS4mWACwA=
=M9og
-----END PGP PUBLIC KEY BLOCK-----
***REMOVED***
Version: GnuPG v1

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
"""
