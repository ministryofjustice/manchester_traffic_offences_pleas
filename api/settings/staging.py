from .docker import *


INSTALLED_APPS.append('raven.contrib.django.raven_compat')

ADMINS = (
    ('[STAGING] HMCTS Reform Sustaining Support', 'sustainingteamdev@hmcts.net'),
)

RAVEN_CONFIG = {
    'dsn': os.environ["SENTRY_DSN"],
    'release': os.environ.get("APP_GIT_COMMIT", "no-git-commit-available")
}
