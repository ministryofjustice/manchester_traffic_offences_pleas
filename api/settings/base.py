from make_a_plea.settings.base import *

ROOT_URLCONF = 'api.urls'

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'make_a_plea.middleware.AdminLocaleURLMiddleware',
    'make_a_plea.middleware.TimeoutRedirectMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
)

PROJECT_APPS = (
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
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

INSTALLED_APPS = INSTALLED_APPS + PROJECT_APPS

del TEMPLATE_CONTEXT_PROCESSORS[TEMPLATE_CONTEXT_PROCESSORS.index('apps.feedback.context_processors.feedback')]

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass
