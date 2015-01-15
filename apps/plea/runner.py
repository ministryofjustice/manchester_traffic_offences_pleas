import os
import sh

from django.test.runner import DiscoverRunner
from django.conf import settings

from .encrypt import clear_user_data


class MAPTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):

        if not os.path.exists(settings.USER_DATA_DIRECTORY):
            os.makedirs(settings.USER_DATA_DIRECTORY)

        if not os.path.exists(settings.GPG_HOME_DIRECTORY):
            os.makedirs(settings.GPG_HOME_DIRECTORY)

        from .encrypt import gpg
        gpg.import_keys(settings.GPG_TEST_KEY)

        super(MAPTestRunner, self).setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):

        super(MAPTestRunner, self).teardown_test_environment(**kwargs)

        clear_user_data()

        print("Removing user data files from {}".format(settings.USER_DATA_DIRECTORY))
