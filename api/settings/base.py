from manchester_traffic_offences.settings.base import *

ROOT_URLCONF = 'api.urls'

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
)

PROJECT_APPS = (
    'moj_template',
    'apps.forms',
    'apps.plea',
    'api',
    'api.v0',
)

# Django-rest-framework throttling config

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
    },
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

INSTALLED_APPS = INSTALLED_APPS + PROJECT_APPS

del TEMPLATE_CONTEXT_PROCESSORS[TEMPLATE_CONTEXT_PROCESSORS.index('apps.feedback.context_processors.feedback')]

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass

# importing test settings file if necessary (TODO could be done better)
if len(sys.argv) > 1 and 'test' or 'harvest' in sys.argv[1]:
    from .testing import *
