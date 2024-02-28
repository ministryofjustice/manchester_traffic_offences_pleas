from .docker import *


INSTALLED_APPS.append('raven.contrib.django.raven_compat')

ADMINS = (
    ('HMCTS Reform Sustaining Support', 'sustainingteamsupport@HMCTS.NET'),
)

ALLOWED_HOSTS = ['prod-api-make-a-plea.apps.live.cloud-platform.service.justice.gov.uk']