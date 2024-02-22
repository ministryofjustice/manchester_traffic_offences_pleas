from .docker import *


INSTALLED_APPS.append('raven.contrib.django.raven_compat')

ADMINS = (
    ('[PREPROD] HMCTS Reform Sustaining Support', 'sustainingteamdev@hmcts.net'),
)

RAVEN_CONFIG = {
    'dsn': os.environ["SENTRY_DSN"],
    'release': os.environ.get("APP_GIT_COMMIT", "no-git-commit-available")
}

ALLOWED_HOSTS = ['preprod-api-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk']