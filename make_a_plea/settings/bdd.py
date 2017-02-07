"""
Settings for running BDD tests
"""
from .local import *
from .testing import *


RECEIPT_ADMIN_EMAIL_ENABLED = False
DEFAULT_FIXTURE_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))),
    "fixtures",
    "bdd_fixtures.json",
)

INSTALLED_APPS.append('django_behave')

TEST_RUNNER = "django_behave.runner.DjangoBehaveOnlyTestSuiteRunner"

TESTING_SERVER_API_PORT = 8190
TESTING_SERVER_API_HOST = "127.0.0.1"
TESTING_SERVER_API_URL = "http://{0}:{1}".format(TESTING_SERVER_API_HOST, TESTING_SERVER_API_PORT)

TESTING_SERVER_APP_PORT = 8100
TESTING_SERVER_APP_HOST = "127.0.0.1"
TESTING_SERVER_APP_URL = "http://{0}:{1}".format(TESTING_SERVER_APP_HOST, TESTING_SERVER_APP_PORT)
