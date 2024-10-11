from make_a_plea.settings.base import *

ROOT_URLCONF = 'api.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'reports',
    'axes'
]

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

PROJECT_APPS = [
    'apps.forms',
    'apps.plea',
    'apps.result',
    'api',
    'api.v0',
]

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    }
]

# Options for Premailer, which inlines the CSS on the fly in email templates and
# makes all URLs absolute
PREMAILER_OPTIONS = {"base_url": os.environ.get("PREMAILER_BASE_URL", "https://www.makeaplea.service.gov.uk"),
                     "remove_classes": False,
                     "keep_style_tags": True,
                     "cssutils_logging_level": logging.ERROR}

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass
