from .docker import *


INSTALLED_APPS.append('raven.contrib.django.raven_compat')

RAVEN_CONFIG = {
    'dsn': os.environ["SENTRY_DSN"],
    'release': os.environ.get("APP_GIT_COMMIT", "no-git-commit-available")
}

