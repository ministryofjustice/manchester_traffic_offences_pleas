import base64
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client

from dateutil.parser import parse as date_parse

from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.test import APITestCase

from apps.plea.models import Case
from .serializers import CaseSerializer


def create_api_user():
    password = "apitest"

    user = User.objects.create(username="apitest",
                               email="test@test.com")

    user.set_password(password)
    user.save()

    credentials = base64.b64encode('{}:{}'.format(user.username, password))

    auth_header = {'HTTP_AUTHORIZATION': 'Basic {}'.format(credentials)}

    return user, auth_header


class GeneralAPiTestCase(APITestCase):

    def setUp(self):
        self.user, self.auth_header = create_api_user()

        self.endpoint = reverse('api-v0:case-list', format="json")

    def test_api_requires_auth(self):

        response = self.client.post('/v0/case/', {}, format='json')

        self.assertEqual(response.status_code, 401)

    def test_every_request_requires_auth(self):

        response = self.client.post(
            '/v0/case/', {}, format='json', **self.auth_header)

        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            '/v0/case/', {}, format='json')

        self.assertEqual(response.status_code, 401)


class CaseAPICallTestCase(APITestCase):

    def setUp(self):
        self.user, self.auth_header = create_api_user()

        self.endpoint = reverse('api-v0:case-list', format="json")

        self.test_data = {
            u'urn': u'00/aa/00000/00'
        }

    def test_urn_validation(self):

        self.test_data['urn'] = 'xxx'

        response = self.client.post(self.endpoint, self.test_data, **self.auth_header)

        self.assertEqual(response.status_code, 400)

        self.test_data['urn'] = '00/aa/0000000/00'
        response = self.client.post(self.endpoint, self.test_data, **self.auth_header)
        self.assertEqual(response.status_code, 201)

        self.test_data['urn'] = 'xxx'
        response = self.client.post(self.endpoint, self.test_data, **self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_valid_submission(self):

        response = self.client.post(self.endpoint, self.test_data, **self.auth_header)

        case = Case.objects.all()[0]

        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(case.urn, self.test_data['urn'])

    def test_valid_submissions_returns_dict(self):
        response = self.client.post(self.endpoint, self.test_data, **self.auth_header)
        self.assertEqual(response.status_code, 201)

        returned_data = json.loads(response.content)

        self.assertEqual(returned_data['urn'], self.test_data['urn'])