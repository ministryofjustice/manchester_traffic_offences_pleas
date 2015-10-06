import os

from redgreenunittest.django.runner import RedGreenDiscoverRunner
from django.conf import settings

from apps.plea.encrypt import clear_user_data, gpg


class MAPTestRunner(RedGreenDiscoverRunner):
    def __init__(self, *args, **kwargs):
        settings.TESTING = True

        super(MAPTestRunner, self).__init__(*args, **kwargs)

    def setup_test_environment(self, **kwargs):

        if not os.path.exists(settings.USER_DATA_DIRECTORY):
            os.makedirs(settings.USER_DATA_DIRECTORY)

        if not os.path.exists(settings.GPG_HOME_DIRECTORY):
            os.makedirs(settings.GPG_HOME_DIRECTORY)

        gpg.import_keys(settings.GPG_TEST_KEY)

        super(MAPTestRunner, self).setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):

        super(MAPTestRunner, self).teardown_test_environment(**kwargs)

        clear_user_data()

        print("Removing user data files from {}".format(settings.USER_DATA_DIRECTORY))
