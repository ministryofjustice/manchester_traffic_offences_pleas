from .base import *

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
DEBUG = True
TESTING = True

try:
    from .local import *
except ImportError:
    pass
