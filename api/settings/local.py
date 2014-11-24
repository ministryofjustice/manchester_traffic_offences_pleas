from .dev import *

ALLOWED_HOSTS = ["localhost", ]
DEBUG = True

#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/Users/ian/Mail'

PLEA_EMAIL_FROM = "ian.george@digital.justice.gov.uk"
PLEA_EMAIL_ATTACHMENT_NAME = "plea.html"
PLEA_EMAIL_TEMPLATE = "plea/plea_email_attachment.html"
PLEA_EMAIL_TO = ["lyndon.garvey@digital.justice.gov.uk", ]
PLEA_EMAIL_BODY = ""

PLEA_CONFIRMATION_EMAIL_FROM = "ian.george@digital.justice.gov.uk"

PLP_EMAIL_TO = ["lyndon.garvey@digital.justice.gov.uk", ]

EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
EMAIL_HOST_USER = 'AKIAJYZQTYYWFQDGROGA'
EMAIL_HOST_PASSWORD = 'AijwCCwF0w6U+jULYNV5L2Ujk3nNn88nGH6NOIg8vUpV'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SMTP_ROUTES["GSI"]["HOST"] = "email-smtp.eu-west-1.amazonaws.com"
SMTP_ROUTES["GSI"]["PORT"] = 587
SMTP_ROUTES["GSI"]["USERNAME"] = "AKIAJYZQTYYWFQDGROGA"
SMTP_ROUTES["GSI"]["PASSWORD"] = "AijwCCwF0w6U+jULYNV5L2Ujk3nNn88nGH6NOIg8vUpV"


SMTP_ROUTES["GMP"]["HOST"] = "email-smtp.eu-west-1.amazonaws.com"
SMTP_ROUTES["GMP"]["PORT"] = 587
SMTP_ROUTES["GMP"]["USERNAME"] = "AKIAJYZQTYYWFQDGROGA"
SMTP_ROUTES["GMP"]["PASSWORD"] = "AijwCCwF0w6U+jULYNV5L2Ujk3nNn88nGH6NOIg8vUpV"

SEND_PLEA_CONFIRMATION_EMAIL = True

DEBUG = True

SERVER_EMAIL = "ian.george@digital.justice.gov.uk"

RECEIPT_INBOX_PASSWORD = "uirpsivcgyilxnay"

RECEIPT_INBOX_FROM_EMAIL = "RoadTrafficPCR@hmcts.gsi.gov.uk"
RECEIPT_INBOX_USERNAME = "makeaplea-receipts@digital.justice.gov.uk"
PLEA_CONFIRMATION_EMAIL_FROM = "no-reply@makeaplea.justice.gov.uk"

USER_SMTP_EMAIL_HOST = "smtp.sendgrid.net"
USER_SMTP_EMAIL_PORT = 587
USER_SMTP_EMAIL_HOST_USERNAME = 'mojdsd'
USER_SMTP_EMAIL_HOST_PASSWORD = 'p8kLodT537!q$'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pleaonline',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}