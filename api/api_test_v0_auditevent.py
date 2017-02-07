"""
Test the AuditEvent feature of the API
"""

import base64
import json

from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.test import (APITestCase, APIRequestFactory, force_authenticate)

from apps.plea.models import AuditEvent, Case, Court, CaseOffenceFilter
from api.v0.views import AuditEventViewSet, CaseViewSet
from api.reusable import create_api_user, create_court


def add_white_list(filter, desc):
    return CaseOffenceFilter.objects.create(filter_match=filter, description=desc)


class GeneralAPITestCase(APITestCase):
    def setUp(self):
        self.user, self.auth_header = create_api_user()

        self.endpoint = reverse('api-v0:case-list', format="json")

    def test_api_requires_auth(self):

        response = self.client.post('/v0/case/', {}, format='json')

        self.assertEqual(response.status_code, 401)

    def test_every_request_requires_auth(self):

        response = self.client.post(
            '/v0/auditevent/', {}, format='json', **self.auth_header)

        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            '/v0/auditevent/', {}, format='json')

        self.assertEqual(response.status_code, 401)


class AuditEventAPICallTestCase(APITestCase):
    """
    Test the AuditEvent api

    TODO: test that methods other than POST fails

    """
    def setUp(self):
        self.user, self.auth_header = create_api_user()
        self.endpoint = reverse('api-v0:auditevent-list', format="json")
        self.test_data = {
            "event_subtype": "EXT1",
            "event_data": {
                "urn": """hdfgT	rv rvjhb <XML!!*(&*&^!^&>"""
            }
        }

    def _post_data(self, data):
        factory = APIRequestFactory()
        request = factory.post(
            "/v0/auditevent/",
            self.test_data,
            format="json",
        )

        force_authenticate(request, self.user)

        auditevent_view = AuditEventViewSet.as_view({"post": "create"})
        response = auditevent_view(request)
        response.render()
        return response

    def test_event_subtype_missing(self):
        data = deepcopy(self.test_data)
        del data['event_subtype']
        response = self._post_data(data)
        self.assertEqual(response.status_code, 400)

    def test_event_subtype_blank(self):
        data = deepcopy(self.test_data)
        data['event_subtype'] = ""
        response = self._post_data(data)
        self.assertEqual(response.status_code, 400)

    def test_event_event_data(self):
        data = deepcopy(self.test_data)
        response = self._post_data(data)
        self.assertEqual(response.status_code, 200)
