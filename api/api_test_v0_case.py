import base64
import json

from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.test import (APITestCase, APIRequestFactory, force_authenticate)

from apps.plea.models import Case, Court, CaseOffenceFilter
from api.v0.views import CaseViewSet


def create_api_user():
    password = "apitest"

    user = User.objects.create(username="apitest",
                               email="user@example.org")

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
        court_email="court@example.org",
        submission_email="court@example.org",
        plp_email="plp@example.org",
        enabled=True,
        test_mode=False)


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

        add_white_list("RT01", "Test RT filter")
        add_white_list("SZ09", "Test RT filter 2")

        self.test_data = {
            u'urn': u'00AA0000000',
            u"ou_code": u"test ou",
            u'case_number': '16273482',
            u'date_of_hearing': u'2016-05-05',
            u'extra_data': {"OrganisationName": "",
                            "Forename1": "Jimmy",
                            "Forename2": "the",
                            "Forename3": "",
                            "Surname": "Dog",
                            "DOB": "1960-1-1",
                            "Gender": "M",
                            "Address1": "",
                            "Address2": "",
                            "Address3": "",
                            "Address4": "",
                            "Address5": "",
                            "Postcode": "",
                            "DriverNumber": "",
                            "NINO": "AB00123456C"},
            u'offences': [
                {
                    u"offence_code": u"RT0123",
                    u"offence_short_title": u"test title",
                    u"offence_wording": u"test title",
                    u"offence_seq_number": u"2"
                },
                {
                    u"offence_code": u"SZ0987",
                    u"offence_short_title": u"test title",
                    u"offence_wording": u"test title",
                    u"offence_seq_number": u"2"
                }
            ]
        }

    def _post_data(self, data):
        factory = APIRequestFactory()

        request = factory.post("/v0/case/", self.test_data,
                               format="json")
        force_authenticate(request, self.user)

        case_view = CaseViewSet.as_view({"post": "create"})
        response = case_view(request)
        response.render()
        return response

    def test_duplicate_submission_validation(self):
        self.test_data['urn'] = '00/aa/0000000/00'
        response = self._post_data(self.test_data)
        self.assertEqual(response.status_code, 201)

        self.test_data['urn'] = '00/aa/0000000/00'
        response = self._post_data(self.test_data)
        self.assertEqual(response.status_code, 201)

    def test_duplicate_submission_with_sent_case(self):
        self.test_data['urn'] = '00/aa/0000000/00'
        response = self._post_data(self.test_data)
        self.assertEqual(response.status_code, 201)
        c = Case.objects.get(urn="00AA000000000")
        c.sent = True
        c.save()

        self.test_data['urn'] = '00/aa/0000000/00'
        response = self._post_data(self.test_data)
        self.assertEqual(response.status_code, 400)

    def test_urn_blank_urn_validation(self):
        self.test_data['urn'] = ""

        response = self._post_data(self.test_data)

        self.assertEqual(response.status_code, 400)

    def test_empty_urn_validation(self):
        del self.test_data['urn']

        response = self._post_data(self.test_data)

        self.assertEqual(response.status_code, 400)

    def test_urn_invalid_format_validation(self):
        self.test_data['urn'] = "aa/00/43224234/aa/25"

        response = self._post_data(self.test_data)

        self.assertEqual(response.status_code, 400)

    def test_valid_submission(self):
        response = self._post_data(self.test_data)

        case = Case.objects.all()[0]

        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(case.offences.all().count(), 2)
        self.assertEqual(case.urn, self.test_data["urn"])

    def test_submission_without_offence_data(self):
        self.test_data["offences"] = []

        response = self._post_data(self.test_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)["non_field_errors"][0], "case has no offences")
        self.assertEquals(Case.objects.count(), 0)

    def test_submission_with_first_non_listed_offence_code(self):
        self.test_data["offences"][0]["offence_code"] = "DF0987"

        response = self._post_data(self.test_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)["non_field_errors"][0], "Case 00AA0000000 contains offence codes [[u'DF09', u'SZ09']] not present in the whitelist")

    def test_submission_with_second_non_listed_offence_code(self):
        self.test_data["offences"][1]["offence_code"] = "DF0987"

        response = self._post_data(self.test_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)["non_field_errors"][0], "Case 00AA0000000 contains offence codes [[u'RT01', u'DF09']] not present in the whitelist")

    def test_submission_with_both_non_listed_offence_codes(self):
        self.test_data["offences"][0]["offence_code"] = "DF0987"
        self.test_data["offences"][1]["offence_code"] = "DF0988"

        response = self._post_data(self.test_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)["non_field_errors"][0], "Case 00AA0000000 contains offence codes [[u'DF09', u'DF09']] not present in the whitelist")

    def test_valid_submissions_returns_dict(self):
        response = self._post_data(self.test_data)

        case = Case.objects.all()[0]

        self.assertEqual(response.status_code, 201)

        returned_data = json.loads(response.content)

        self.assertEqual(returned_data['urn'], self.test_data['urn'])
