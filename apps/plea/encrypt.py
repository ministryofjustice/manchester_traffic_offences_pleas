import gnupg
import json
import os
import time
import logging

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


gpg = gnupg.GPG(gnupghome=settings.GPG_HOME_DIRECTORY)
gpg.encoding = 'utf-8'


class PersistenceError(Exception):
    pass

logger = logging.getLogger(__name__)

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

    logger.warning("encrypt_and_store_user_data urn: {} case: {}".format(urn,case_id))

    file_name = "{}_[{}]_{}.data.gpg".format(urn.replace('/', '-').upper(), case_id,
                                        str(time.time()).replace('.', '_'))
    logger.warning("encrypt_and_store_user_data: file_name: {}".format(file_name))

    file_path = os.path.join(settings.USER_DATA_DIRECTORY, file_name)
    logger.warning("encrypt_and_store_user_data: file_path: {}".format(file_path))

    data = json.dumps(data, cls=DjangoJSONEncoder)
    h = open("before_gpg.encrypt.txt", "w")
    h.write(data)
    h.flush()
    h.close()

    logger.warning("encrypt_and_store_user_data: about to encrypt data")

    # Check if the recipient's key is available
    recipient_key = gpg.list_keys(settings.GPG_RECIPIENT)
    if not recipient_key:
        logger.error("encrypt_and_store_user_data: invalid recipient: {}".format(settings.GPG_RECIPIENT))
        raise PersistenceError("GPG encryption failed: invalid recipient")

    encrypted_data = gpg.encrypt(data, settings.GPG_RECIPIENT, always_trust=True)
    logger.warning("encrypt_and_store_user_data: encrypted_data.status {}".format(encrypted_data.status))

    if encrypted_data.status != "encryption ok":
        logger.error("encrypt_and_store_user_data: encrypted_data.status {}".format(encrypted_data.status))
        raise PersistenceError(
            "GPG encryption failed: {}".format(encrypted_data.status))

    try:
        logger.warning("encrypt_and_store_user_data: creating file {}".format(file_path))
        fd = os.open(file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        logger.warning("encrypt_and_store_user_data: file created")
        os.write(fd, str(encrypted_data).encode())
        logger.warning("encrypt_and_store_user_data: file write")

        # NOTE: It seems unlikely that there'll be file name
        # clashes given the file name is the urn + timestamp. However,
        # if it does become an issue, you can check for a 'file already
        # exists' error by captching an OSError with ex.errno == 17
    except Exception as e:
        logger.error("encrypt_and_store_user_data fd file error: {}".format(e))

    finally:
        if 'fd' in locals():
            logger.warning("encrypt_and_store_user_data: closing file")
            os.close(fd)
