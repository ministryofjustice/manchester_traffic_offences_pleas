from .base import *

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
DEBUG = True
TESTING = True

# Provide a working cookie key
ENCRYPTED_COOKIE_KEYS = [
    os.environ.get("ENCRYPTED_COOKIE_KEY", "dJa1JYaaddz5OafOXfqEj7wRVcmZ7Iz5xTI0hVI0Iwo=")
]

try:
    from .local import *
except ImportError:
    pass
