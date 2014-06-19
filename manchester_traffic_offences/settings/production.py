from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Sym Roe', 'sym.roe@digital.justice.gov.uk'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manchester_traffic_offences',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}