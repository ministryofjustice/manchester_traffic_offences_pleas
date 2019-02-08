"""
Test the AuditEvent feature of the API
"""
import json
from copy import deepcopy
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
        self.endpoint = reverse('api-v0:auditevent-list', format="json")
        self.test_data = {
            "event_type": "auditevent_api",
            "event_subtype": "not_set",
        }

    def tearDown(self):
        AuditEvent.objects.all().delete()
        Case.objects.all().delete()
        Court.objects.all().delete()
        CaseOffenceFilter.objects.all().delete()

    def test_api_no_auth_fails(self):

        response = self.client.post(
            self.endpoint,
            self.test_data,
            format='json')
        self.assertEqual(response.status_code, 401)

    def test_api_with_auth_succeeds(self):
        response = self.client.post(
            self.endpoint,
            self.test_data,
            format='json',
            **self.auth_header)
        self.assertEqual(response.status_code, 201)


class AuditEventAPICallTestCase(APITestCase):
    """
    Test the AuditEvent API.

    TODO: test that methods other than POST fails

    """
    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user, self.auth_header = create_api_user()
        self.endpoint = reverse('api-v0:auditevent-list', format="json")
        self.test_data = {
            "event_type": "auditevent_api",
            "event_subtype": "EXT1",
            "event_data": json.dumps(
                {
                    "urn": """hdfgT	rv rvjhb <XML!!*(&*&^!^&>""",
                    "Forename1": "Alice",
                    "Forename2": "Alexa",
                    "Surname": "Alexandra",
                    "DOB": "1976-11-19T00:00:46",
                    "Gender": "N",
                    "Address1": "200 Triumph Boulevard",
                    "Address2": "Harley St",
                    "PostCode": "F9 6Y",
                    "DateOfHearing": "2017-03-31T21:10:28",
                }
            ),
        }

    def _post_data(self, data, fake_auth=True):
        request = self.request_factory.post(
            "/v0/auditevent/",
            data=data,
            format="json",
        )

        if fake_auth:
            force_authenticate(request, self.user)

        auditevent_view = AuditEventViewSet.as_view({"post": "create"})
        response = auditevent_view(request)
        response.render()

        return response

    def test_event_type_missing(self):

        data = deepcopy(self.test_data)
        del data["event_type"]
        response = self._post_data(data)
        response_json = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response_json,
            {u'event_type': [u'This field is required.']})


    def test_event_subtype_missing(self):

        data = deepcopy(self.test_data)
        del data["event_subtype"]
        response = self._post_data(data)
        response_json = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response_json,
            {u'event_subtype': [u'This field is required.']})

    def test_event_type_blank(self):

        data = deepcopy(self.test_data)
        data["event_type"] = ""
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {"event_type": [u'"" is not a valid choice.']})

    def test_event_subtype_blank(self):
        data = deepcopy(self.test_data)
        data["event_subtype"] = ""
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {'event_subtype': [u'"" is not a valid choice.']})

    def test_success(self):
        count = AuditEvent.objects.count()
        data = deepcopy(self.test_data)
        response = self._post_data(data)
        response_json = json.loads(response.content.decode('utf-8'))
        _id = int(response_json["id"])
        saved_item = AuditEvent.objects.get(id=_id)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AuditEvent.objects.count(), count + 1)
        self.assertEqual(
            saved_item,
            AuditEvent.objects.order_by("-event_datetime")[0])
        self.assertEqual(
            response.data,
            {
                'event_trace': None,
                'event_type': 'auditevent_api',
                'event_subtype': 'EXT1',
                'id': saved_item.id,
                'event_datetime': saved_item.event_datetime.isoformat(),
            }
        )
