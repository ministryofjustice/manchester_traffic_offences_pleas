# coding=utf-8
from datetime import date, timedelta
import base64
import json

from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.test import (APITestCase, APIRequestFactory, force_authenticate)

from apps.result.models import Result
from apps.plea.models import Court
from api.v0.views import ResultViewSet

from api.reusable import create_api_user, create_court


def create_api_user():
    password = "apitest"

    user = User.objects.create(username="apitest",
                               email="user@example.org")

    user.set_password(password)
    user.save()

    credentials = base64.b64encode("{}:{}".format(user.username, password))

    auth_header = {"HTTP_AUTHORIZATION": "Basic {}".format(credentials)}

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


class GeneralAPITestCase(APITestCase):
    def setUp(self):
        self.user, self.auth_header = create_api_user()

        self.endpoint = reverse("api-v0:result-list", format="json")

    def test_api_requires_auth(self):
        response = self.client.post("/v0/result/", {}, format="json")

        self.assertEqual(response.status_code, 401)

    def test_every_request_requires_auth(self):
        response = self.client.post(
            "/v0/result/", {}, format="json", **self.auth_header)

        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/v0/result/", {}, format="json")

        self.assertEqual(response.status_code, 401)


class CaseAPICallTestCase(APITestCase):
    def setUp(self):
        create_court("51")
        self.user, self.auth_header = create_api_user()

        self.endpoint = reverse("api-v0:result-list", format="json")

        self.test_data = {
            u"urn": u"51AA0000000",
            u"case_number": u"16273482",
            u"date_of_hearing": unicode(date.today() + timedelta(days=5)),
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

    def _post_data(self, data):
        factory = APIRequestFactory()

        request = factory.post("/v0/case/", self.test_data,
                               format="json")
        force_authenticate(request, self.user)

        result_view = ResultViewSet.as_view({"post": "create"})
        response = result_view(request)
        response.render()
        return response

    def test_urn_blank_urn_validation(self):
        self.test_data["urn"] = ""

        response = self.client.post(self.endpoint, self.test_data,
                                    **self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_duplicate_submission_validation(self):
        response = self._post_data(self.test_data)
        self.assertEqual(response.status_code, 201)

        response = self._post_data(self.test_data)
        self.assertEqual(response.status_code, 201)

    def test_empty_urn_validation(self):
        del self.test_data["urn"]

        response = self.client.post(self.endpoint, self.test_data,
                                    **self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_urn_invalid_format_validation(self):
        self.test_data["urn"] = "aa/00/43224234/aa/25"

        response = self.client.post(self.endpoint, self.test_data,
                                    **self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_valid_submission(self):
        factory = APIRequestFactory()
        request = factory.post("/v0/result/", json.dumps(self.test_data),
                               content_type="application/json")
        force_authenticate(request, self.user)

        result_view = ResultViewSet.as_view({"post": "create"})

        response = result_view(request)

        result = Result.objects.all()[0]

        self.assertEqual(Result.objects.all().count(), 1)
        self.assertEqual(result.result_offences.all().count(), 2)
        self.assertEqual(result.urn, self.test_data["urn"])

        self.assertEquals(result.urn, self.test_data["urn"])

    def test_submission_without_offence_data(self):
        self.test_data["result_offences"] = []

        factory = APIRequestFactory()

        request = factory.post("/v0/result/", json.dumps(self.test_data),
                               content_type="application/json")
        force_authenticate(request, self.user)

        result_view = ResultViewSet.as_view({"post": "create"})

        result_view(request)

        result = Result.objects.all()[0]

        self.assertEquals(result.result_offences.all().count(), 0)

    def test_valid_submissions_returns_dict(self):
        response = self.client.post(self.endpoint, self.test_data,
                                    **self.auth_header)
        self.assertEqual(response.status_code, 201)

        returned_data = json.loads(response.content)

        self.assertEqual(returned_data["urn"], self.test_data["urn"])
