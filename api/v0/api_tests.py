import base64
import json

from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.test import (APITestCase, APIRequestFactory, force_authenticate)

from apps.plea.models import Case, Court
from .views import CaseViewSet


def create_api_user():
    password = "apitest"

    user = User.objects.create(username="apitest",
                               email="test@test.com")

    user.set_password(password)
    user.save()

    credentials = base64.b64encode('{}:{}'.format(user.username, password))

    auth_header = {'HTTP_AUTHORIZATION': 'Basic {}'.format(credentials)}

    return user, auth_header


def create_court(region):
    return Court.objects.create(
        court_code="0000",
        region_code=region,
        court_name="test court",
        court_address="test address",
        court_telephone="0800 MAKEAPLEA",
        court_email="test@test.com",
        submission_email=True,
        plp_email="test@test.com",
        enabled=True,
        test_mode=False)


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
        create_court("00")
        self.user, self.auth_header = create_api_user()

        self.endpoint = reverse('api-v0:case-list', format="json")

        self.test_data = {
            u'urn': u'00AA0000000',
            u'case_number': '16273482',
            u'offences': [
                {
                    u"ou_code": u"test ou",
                    u"offence_code": u"test",
                    u"offence_short_title": u"test title",
                    u"offence_wording": u"test title",
                    u"offence_seq_number": u"2"
                },
                {
                    u"ou_code": u"test ou2",
                    u"offence_code": u"test",
                    u"offence_short_title": u"test title",
                    u"offence_wording": u"test title",
                    u"offence_seq_number": u"2"
                }
            ]
        }

    def test_urn_dupe_validation(self):
        self.test_data['urn'] = '00/aa/0000000/00'
        response = self.client.post(self.endpoint, self.test_data,
                                    **self.auth_header)

        self.assertEqual(response.status_code, 201)

        self.test_data['urn'] = '00/aa/0000000/00'
        response = self.client.post(self.endpoint, self.test_data,
                                    **self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_valid_submission(self):

        factory = APIRequestFactory()
        request = factory.post("/v0/case/", json.dumps(self.test_data),
                               content_type="application/json")
        force_authenticate(request, self.user)

        case_view = CaseViewSet.as_view({"post": "create"})

        case_view(request)

        case = Case.objects.all()[0]

        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(case.offences.all().count(), 2)
        self.assertEqual(case.urn, self.test_data["urn"])

        self.assertEquals(case.urn, self.test_data["urn"])

    def test_submission_without_offence_data(self):
        self.test_data["offences"] = []

        factory = APIRequestFactory()

        request = factory.post("/v0/case/", json.dumps(self.test_data),
                               content_type="application/json")
        force_authenticate(request, self.user)

        case_view = CaseViewSet.as_view({"post": "create"})

        case_view(request)

        case = Case.objects.all()[0]

        self.assertEquals(case.offences.all().count(), 0)

    def test_valid_submissions_returns_dict(self):
        response = self.client.post(self.endpoint, self.test_data,
                                    **self.auth_header)
        self.assertEqual(response.status_code, 201)

        returned_data = json.loads(response.content)

        self.assertEqual(returned_data['urn'], self.test_data['urn'])
