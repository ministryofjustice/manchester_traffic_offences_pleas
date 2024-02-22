from .docker import *


INSTALLED_APPS.append('raven.contrib.django.raven_compat')

ADMINS = (
    ('[PREPROD] HMCTS Reform Sustaining Support', 'sustainingteamdev@hmcts.net'),
)

ALLOWED_HOSTS = ['preprod-api-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk']