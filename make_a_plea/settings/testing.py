import os

from .base import *

logging.disable(logging.CRITICAL)

ADMINS = (
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk'),
    ('Ian George', 'ian.george@digital.justice.gov.uk'),
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

EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'

DEBUG = False

SECRET_KEY = "fjsklfosufcilsft37dGDRR%^$%^^gfsdvf"

# the test user data directory
USER_DATA_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_user_data')
GPG_HOME_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_gpg_home')
GPG_RECIPIENT = "test@example.org"

TEST_RUNNER = 'make_a_plea.runner.MAPTestRunner'

ENCRYPTED_COOKIE_KEYS = [
    '9evXbsR_1yZA5EW_blSI4O69MjGKwOu1-UwLK_PWyKw=',
]

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
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG v1

lQHYBFaKcs0BBADV9YLplRIJdZ+6blFnFlN2zb4XHnqky1Q4VfmC/P8lUqdoiYz7
2dNTdDq+bVbFYUNMHJ37A/AoRkMfkRYjYyiyok9OfUVcTv/+ha/03h0kcdAnH0I0
gWoGwovXkbdSWzOAVwjvBpes3d5DCvQe655rzBjR33s45lmsiQPpMamnhQARAQAB
AAP6AvZRMlaurJQvpURzEBBOZi4BsbmUTRpw4g7JU4zueLUk6DJEp2qj8wXVl7P/
0t++hMaTUVmum4Ai3G8FIBxMAJagIXCD0tHe7UikPjavx27kE+8d354KWntYdc+/
PtAv8euT+5OcbXQQKDCA9oFOiHR+7yRKwT9oT2Mryf/8fkkCANi6LMD5Ol4HeNqW
U2WnVIdTg7n0Yb5qEuRH9v7SRlRcaqC/ucl6/Ya3zZ5J+JAHWoLXOR57t6wSRnoO
ysC1ltcCAPy668H1y7DmtA/dkxnZeEMHyQ3kqHbUKrB62e6TcWIKl9JW/UzpOOOU
nL0IelxtAEFXJFojX4Mye9YCJLY41QMCAPnCtoqQSAxzIoQ0Y5H6g0sNtsu5AqTN
phb0NbqmYkRUnP9HTUj4pB7rCJ4+JpavSxs7X93M8M/vVYnYLPgXwqqlNbQcVGVz
dCBVc2VyIDx0ZXN0QGV4YW1wbGUub3JnPoi4BBMBAgAiBQJWinLNAhsDBgsJCAcD
AgYVCAIJCgsEFgIDAQIeAQIXgAAKCRCSpC5gPJPqbhcQBACgLEbcTEbTsUVGH9XW
Pz56tsj1TO9ieZVYGeqhFsuTxjr4h02eZx1YLmKRRwQE1N1TY1v8npM4vcEg1PCV
n7QlUklIxTq4bXwP+N7al5ZZr2xWeFUhkMQbCZ2rb13F0Pp5Lj875JDHehjH4G5M
mKpOqwFG9kHZ5UVLJS8apRT9jJ0B2ARWinLNAQQAwA+t/c4tXLXjX8NMKRmQPa3D
P2hZbjfNSimzQjhwjE8r5EWj7962M+JSiXpSl+fK9Hvyjif282/+R/SJc2QCqbeN
fHKFPjjJS7PU1QikuNHKuFv3sw/+0vm0NXsuuRZkOkfseqdSvgmdoo3Q7eBw+HD3
xZbDjA6pMqRWZ9Et0KMAEQEAAQAD/1IeIiFzpxeNuWL3iLfF81M72VBiGGK0vzSn
cbqtkQmczEJ0uCxWSAcVDH81at0CQVeZK1M2qTLavpkbaC2LJEuX+uAkbrVtLEqe
qHeXrLNJ42k2HoqO33ZmZnI8V5Aj9IK8zHsOqfG5tHfW9PXFMA/7FnxaPRUj6W6D
nB12sFaJAgDJ9FU8GLqlN5/G3Qp1qMJso1i9y39G08oO0YcUXmWHv+ri9QJwNInj
ZhD4+qTT4DvUUdUWpVu+kvVleMftbSKPAgDzdZOSamn6esT+zPWc0i8RzLT2Ke4s
wBhsLfvJF3R12ZNrE6DJd7b4kAvA2NY3n/ldbpI82HWSrIp4ypf2HiqtAgDIICBw
//i9PTINv5iA4Bk5FKJ2A0tN+9BvCDtI82sewz0XS+yfPqyVEPsS4ADOTRTMWbVO
sLSDKr+i94CIwLjhpN2IngQYAQIACQUCVopyzQIbDAAKCRCSpC5gPJPqbsczA/iX
tmOUONd9kzRYFNRsjcbrkahWJ7vObS1V0kQvs3PKM7IdNtuoTdnugxOabbXvhz1h
w3QPwJipoPkh8CcilnUbGKNsEwA43F8ecIvtJuuDFnBRW9XqQmAymTpa8jra3XXm
d1+uZ6Nz/8DLcYnAWbhWeP1w66UAjsoGEuJlgAsA
=NAq1
-----END PGP PRIVATE KEY BLOCK-----
"""
