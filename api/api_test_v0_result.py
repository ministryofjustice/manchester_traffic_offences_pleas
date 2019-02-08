# coding=utf-8
from copy import deepcopy
from datetime import date, timedelta
import json

from rest_framework.reverse import reverse
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    force_authenticate)

from api.reusable import create_api_user, create_court
from api.v0.views import ResultViewSet
from apps.plea.models import AuditEvent, Court
from apps.result.models import Result


class GeneralAPITestCase(APITestCase):

    def setUp(self):
        self.user, self.auth_header = create_api_user()
        self.endpoint = reverse("api-v0:result-list", format="json")

    def test_auth_succeeds(self):
        response = self.client.post(
            self.endpoint,
            {},
            format="json",
            **self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_no_auth_fails(self):
        response = self.client.post(
            self.endpoint,
            {},
            format="json")
        self.assertEqual(response.status_code, 401)


class CaseAPICallTestCase(APITestCase):

    def setUp(self):
        self.user, self.auth_header = create_api_user()
        self.endpoint = reverse("api-v0:result-list", format="json")
        self.request_factory = APIRequestFactory()

        create_court("51")
        self.test_data = {
            u"urn": u"51AA0000000",
            u"case_number": u"16273482",
            u"date_of_hearing": str(date.today() + timedelta(days=5)),
            u"ou_code": u"123",
            u"result_offences": [
                {u"offence_code": u"CODE123",
                 u"offence_seq_number": u"001",
                 u"offence_data": [
                     {u"result_code": u"F0123",
                      u"result_short_title": u"Testing the results importer",
                      u"result_wording": u"Wording with cash value of £123.00",
                      u"result_seq_number": u"001"}]},
                {u"offence_code": u"CODE321",
                 u"offence_seq_number": u"002",
                 u"offence_data": [
                     {u"result_code": u"F3210",
                      u"result_short_title": u"Testing the results importer",
                      u"result_wording": u"Wording with cash value of £321.00",
                      u"result_seq_number": u"002"}]}
            ]
        }

    def tearDown(self):
        AuditEvent.objects.all().delete()
        Court.objects.all().delete()
        Result.objects.all().delete()

    def _post_data(self, data):
        request = self.request_factory.post(
            self.endpoint,
            data=data,
            format="json")
        force_authenticate(request, self.user)
        result_view = ResultViewSet.as_view({"post": "create"})
        response = result_view(request)
        response.render()
        return response

    def test_urn_blank_urn_validation(self):
        data = deepcopy(self.test_data)
        data["urn"] = ""
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {"urn": ["This field may not be blank."]})

    def test_duplicate_submissions_succeeds(self):
        response1 = self._post_data(self.test_data)
        response2 = self._post_data(self.test_data)

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)

    def test_missing_urn_validation(self):
        data = deepcopy(self.test_data)
        del data["urn"]
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {"urn": ["This field is required."]})

    def test_urn_invalid_format_validation(self):
        data = deepcopy(self.test_data)
        data["urn"] = "aa/00/43224234/aa/25"
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {'urn': [u'The URN is not valid']})

    def test_valid_submission(self):
        data = deepcopy(self.test_data)
        response = self._post_data(data)
        result = Result.objects.all()[0]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Result.objects.all().count(), 1)
        self.assertEqual(result.result_offences.all().count(), 2)
        self.assertEqual(result.urn, self.test_data["urn"])

    def test_submission_without_offence_data_succeeds(self):
        data = deepcopy(self.test_data)
        data["result_offences"] = []
        response = self._post_data(data)
        result = Result.objects.all()[0]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(result.result_offences.all().count(), 0)

    def test_valid_submissions_returns_dict_with_correct_urn(self):
        response = self._post_data(self.test_data)
        returned_data = json.loads(response.content.decode())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(type(returned_data), dict)
        self.assertEqual(returned_data["urn"], self.test_data["urn"])
