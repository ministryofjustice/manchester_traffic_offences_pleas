from .base import *

ADMINS = (
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk'),
    ('Ian George', 'ian.george@digital.justice.gov.uk'),
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

TESTING = True
DEBUG = False

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
SECRET_KEY = "fjsklfosufcilsft37dGDRR%^$%^^gfsdvf"

# the test user data directory
USER_DATA_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_user_data')
GPG_HOME_DIRECTORY = os.path.join(PROJECT_ROOT, 'test_gpg_home')
GPG_RECIPIENT = "test@test.com"

TEST_RUNNER = 'apps.plea.runner.MAPTestRunner'

# a test gpg key with no passphrase and email test@test.com

GPG_TEST_KEY = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1

mI0EVK1D1QEEAL6bi8YLMPid4eDaPnxB0SJExucB5mrTF13xU8UC8GoTpkltTlxy
w3JL21COAsFCxVLPJE98PG2X3R1Mi7MohfXxAANrUpxavRgE68NWEaoAimnsw01R
+vXQTYk90u6xDW61FHFsSNDDvUPzToa9pIrud1JMSMCHwcHbsSbke6LlABEBAAG0
GVRlc3QgVXNlciA8dGVzdEB0ZXN0LmNvbT6IuAQTAQIAIgUCVK1D1QIbAwYLCQgH
AwIGFQgCCQoLBBYCAwECHgECF4AACgkQVAuHyYiqXRcwfQP+J/s4X3qtMKW4rmQG
HHu8AzJ2PxWZIk1DCSy9HZ7VtsGFOSIPE+71/P2c278yzZQaZ54ALeSmT6Kv/xxj
nNDUtamUr/42Dpa+Mn3V1U6SOe5G2wTXdkv+hztpooltt0X0TIUw86wclZAvx93e
1Z4KSQ1tWuc/32YN3VdhrnmSiAO4jQRUrUPVAQQApow0RnvNCJ0YKOEeue6HML29
+leauU3W+jWuhqlmgQkTJdhPtD8UBI73DcAUGox427uqnnmeyLReiUCbImW1kCFq
+fSoXEePjNOudo5d4+bo5MiJYnY+5yHUftg71pq744DsolcoxlegM5PJMwgnnKUf
mDoViGS9yP+ZEp7V0+cAEQEAAYifBBgBAgAJBQJUrUPVAhsMAAoJEFQLh8mIql0X
ocID/0b1CbL8PvWV0rA3JGSPl3jR81YJk4yT/VMBjXGa0ohgleV7a3Hs/AyjYvnP
P6/lTAvZ14AoniTzARsz8w67mKvbWLY84jSq9rqBzDipUJkbhJiGZN9jcx82Wr8z
NkT+CFXufdUVzyb26FYtY0bMfY4io3X7tVTBODGMmpnmE4bM
=PQK0
-----END PGP PUBLIC KEY BLOCK-----
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG v1

lQHYBFStQ9UBBAC+m4vGCzD4neHg2j58QdEiRMbnAeZq0xdd8VPFAvBqE6ZJbU5c
csNyS9tQjgLBQsVSzyRPfDxtl90dTIuzKIX18QADa1KcWr0YBOvDVhGqAIpp7MNN
Ufr10E2JPdLusQ1utRRxbEjQw71D806GvaSK7ndSTEjAh8HB27Em5Hui5QARAQAB
AAP+KbF9lA77oc5rS9OBao29ENlphrtwKvrMuDRjJgucCiANNi+OPgOug/Ba41aE
/MA9yHzeDPL4huJ6r/9/6WsaTg6bcNJ/3La7nPsKfA2tM2d9ri3dhJtDJ65leNPJ
7G3jzlQxjT5YvbXN1OKsLjEt1hMkR0LymlydspubFqa6OGsCAM+R3XoDAk1QBxWb
KyIPRbdDRTNCriduilYepOexma00XENG4pF1GMZCMiMuSdqXvXP+klb99dLoZVQ9
sKFFVPMCAOsUh8AsCMKNMD7jv/FXfdHFsIFmE6Ep/22OFCnvym7kYYunejsbgYOl
OC4p605kfRna2CIwYjLqNxW6sSbdfscCAI5mK9Uooe0FHAXtLrtfQHK7b7LLrHPU
2TWMTYIur5fUibFy2ySrXdxqf5Tta+bW3NoUSYVskhHDhk60v75E8w2g57QZVGVz
dCBVc2VyIDx0ZXN0QHRlc3QuY29tPoi4BBMBAgAiBQJUrUPVAhsDBgsJCAcDAgYV
CAIJCgsEFgIDAQIeAQIXgAAKCRBUC4fJiKpdFzB9A/4n+zhfeq0wpbiuZAYce7wD
MnY/FZkiTUMJLL0dntW2wYU5Ig8T7vX8/ZzbvzLNlBpnngAt5KZPoq//HGOc0NS1
qZSv/jYOlr4yfdXVTpI57kbbBNd2S/6HO2miiW23RfRMhTDzrByVkC/H3d7VngpJ
DW1a5z/fZg3dV2GueZKIA50B2ARUrUPVAQQApow0RnvNCJ0YKOEeue6HML29+lea
uU3W+jWuhqlmgQkTJdhPtD8UBI73DcAUGox427uqnnmeyLReiUCbImW1kCFq+fSo
XEePjNOudo5d4+bo5MiJYnY+5yHUftg71pq744DsolcoxlegM5PJMwgnnKUfmDoV
iGS9yP+ZEp7V0+cAEQEAAQAD/RY0+qFtT3z3CWol/kVXd0I6ApNXTAOqS+Bn+QHu
o4LQFXQF4DbN9FrZPzrfoi6aDWFrKAhiehgT6MkPSsAu5KMAoG5HnaslWIrpH7fj
vLQTk3QBPEIeLz4EXOEPa38gAhulwfWyI/tRolgGguGL5Sn5GBeB2IDv+cSy80Q3
oBPtAgDHY8XDoJLqZFK70I6XqFOjMAbUFNVul+9yJyPN/rLWRi+iWPZoV9Ol0dIA
B68M7ltTsu5Pou5RXOq5vmn5BKNTAgDV1V/tteXHwWsOV4qOS/zL9e5xXTxhco08
yF5TteyiBBMsD4jzcJEIvHoSlFrImDiJVVOoF7utrCrnZC6p8G6dAf9nxH+16z1j
ODNjLGVZ5EAa9lEZPWpbS4TAL7jsK0o023vyxnkTgNnU3zKQwWqfG7hk8+smpuAD
otr717WkrDvWouuInwQYAQIACQUCVK1D1QIbDAAKCRBUC4fJiKpdF6HCA/9G9Qmy
/D71ldKwNyRkj5d40fNWCZOMk/1TAY1xmtKIYJXle2tx7PwMo2L5zz+v5UwL2deA
KJ4k8wEbM/MOu5ir21i2POI0qva6gcw4qVCZG4SYhmTfY3MfNlq/MzZE/ghV7n3V
Fc8m9uhWLWNGzH2OIqN1+7VUwTgxjJqZ5hOGzA==
=Nx2Y
-----END PGP PRIVATE KEY BLOCK-----
"""
