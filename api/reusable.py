"""
Reuasable
=========

Test code that can be re-used.

TODO: move tests into their own directory

"""
import base64

from django.contrib.auth.models import User

from apps.plea.models import Case, Court, CaseOffenceFilter
from api.v0.views import CaseViewSet


def create_api_user():
    password = "apitest"

    user = User.objects.create(username="apitest",
                               email="user@example.org")

    user.set_password(password)
    user.save()

    credentials = base64.b64encode('{}:{}'.format(user.username, password).encode("utf-8"))

    auth_header = {'HTTP_AUTHORIZATION': 'Basic {}'.format(credentials.decode())}
    return user, auth_header


def create_court(region):
    return Court.objects.create(
        court_code="0000",
        region_code=region,
        court_name="test court",
        court_address="test address",
        court_telephone="0800 MAKEAPLEA",
        court_email="court@example.org",
        submission_email="court@example.org",
        plp_email="plp@example.org",
        enabled=True,
        test_mode=False)
