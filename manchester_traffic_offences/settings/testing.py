from .base import *

ADMINS = (
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk'),
)

LETTUCE_AVOID_APPS = (
    'south',
    'moj_template',
    'django_extensions',
    'testing',
)
LETTUCE_SERVER_PORT = 8100

TESTING = True

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

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