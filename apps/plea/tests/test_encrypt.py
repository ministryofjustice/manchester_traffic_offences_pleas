from django.test import TestCase

from apps.plea.encrypt import clear_user_data

import tempfile
import os
import shutil


def write_files(test_dir, *paths):
    for path in paths:
        with open(os.path.join(test_dir, path), 'w+') as f:
            f.write('1')


class TestEncrypt(TestCase):
    def test_clear_user_data(self):
        test_dir = tempfile.mkdtemp()
        write_files(test_dir, 'file1', 'file2')

        with self.settings(USER_DATA_DIRECTORY=test_dir):
            clear_user_data()
            self.assertEquals(os.listdir(test_dir), [])

        shutil.rmtree(test_dir)

