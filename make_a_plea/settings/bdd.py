from .testing import *


INSTALLED_APPS.append('django_behave')

TEST_RUNNER="django_behave.runner.DjangoBehaveOnlyTestSuiteRunner"

