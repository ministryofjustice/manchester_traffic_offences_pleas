import gnupg
import json
import os
import time

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


gpg = gnupg.GPG(gnupghome=settings.GPG_HOME_DIRECTORY)
gpg.encoding = 'utf-8'


class PersistenceError(Exception):
    pass


def clear_user_data():
    """
    Empty the user data directory
    """

    for path in os.listdir(settings.USER_DATA_DIRECTORY):
        os.unlink(os.path.join(settings.USER_DATA_DIRECTORY, path))


def encrypt_and_store_user_data(urn, case_id, data, user_data_directory=None):
    """
    Encrypt user data and persist to disc.

    args:
        urn - the URN for the case
        data - a json-able dict containing the user data

    uses the following settings:
        settings.USER_DATA_DIRECTORY the path that user data is persisted to
        settings.GPG_RECIPIENT
        settings.GPG_HOME_DIRECTORY

    an encrypted file is created in the settings.USER_DATA_PATH directory
    with the format:

    {urn}-{unixepochtime}.data.gpg

    """

    file_name = "{}_[{}]_{}.data.gpg".format(urn.replace('/', '-').upper(), case_id,
                                        str(time.time()).replace('.', '_'))

    file_path = os.path.join(settings.USER_DATA_DIRECTORY, file_name)

    data = json.dumps(data, cls=DjangoJSONEncoder)

    encrypted_data = gpg.encrypt(data, settings.GPG_RECIPIENT, always_trust=True)

    if encrypted_data.status != "encryption ok":
        raise PersistenceError(
            "GPG encryption failed: {}".format(encrypted_data.status))

    try:
        fd = os.open(file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(encrypted_data).encode())

        # NOTE: It seems unlikely that there'll be file name
        # clashes given the file name is the urn + timestamp. However,
        # if it does become an issue, you can check for a 'file already
        # exists' error by captching an OSError with ex.errno == 17

    finally:
        if 'fd' in locals():
            os.close(fd)
