from manchester_traffic_offences.settings.base import *

ROOT_URLCONF = 'api.urls'

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.formtools',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'south',
    'django_extensions',
    'rest_framework',
)

PROJECT_APPS = (
    'moj_template',
    'apps.govuk_utils',
    'apps.plea',
    'api.v0',
)

SMTP_ROUTES = {"GSI": {"HOST": "localhost",
                       "PORT": 25},
               "GMP": {"HOST": "localhost",
                       "PORT": 25}}

handler500 = 'api.views.api_500'

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
