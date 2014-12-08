from .base import *

ADMINS = (
    ('Lyndon Garvey', 'lyndon.garvey@digital.justice.gov.uk'),
)

LETTUCE_AVOID_APPS = (
    'south',
    'moj_template',
    'django_extensions',
    'testing',
)
LETTUCE_SERVER_PORT = 8100

TESTING = True
