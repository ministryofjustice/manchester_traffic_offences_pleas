from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

ALLOWED_HOSTS = ["api.makeaplea.dsd.io", ]
