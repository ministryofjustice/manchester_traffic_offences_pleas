from copy import deepcopy
import json

from django.contrib.auth.models import User

from rest_framework.reverse import reverse
from rest_framework.test import (APITestCase, APIRequestFactory, force_authenticate)

from apps.plea.models import AuditEvent, Case, Court, CaseOffenceFilter
from api.v0.views import CaseViewSet
from api.reusable import create_api_user, create_court


def add_white_list(filter, desc):
    return CaseOffenceFilter.objects.create(filter_match=filter, description=desc)


class GeneralAPITestCase(APITestCase):

    def setUp(self):
        self.user, self.auth_header = create_api_user()
        self.endpoint = reverse('api-v0:case-list', format="json")

    def test_api_no_auth_fails(self):
        response = self.client.post(
            self.endpoint,
            {},
            format='json')

        self.assertEqual(response.status_code, 401)

    def test_api_with_auth_succeeds(self):

        response = self.client.post(
            self.endpoint,
            {},
            format='json',
            **self.auth_header)

        self.assertEqual(response.status_code, 400)

    def test_unsupported_methods_fail(self):

        for method in ["put", "get", "patch", "head", "delete"]:
            client_method = getattr(self.client, method)
            response = client_method(
                self.endpoint,
                {},
                format='json',
                **self.auth_header)
            self.assertEqual(response.status_code, 405)


class CaseAPICallTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
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
            u'initiation_type': u'J',
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

    def _post_data(self, data, force_auth=True):

        request = self.factory.post(
            self.endpoint,
            data=data,
            format="json",
        )

        if force_auth:
            force_authenticate(request, self.user)

        case_view = CaseViewSet.as_view({"post": "create"})
        response = case_view(request)
        response.render()
        return response

    def test_duplicate_submission_validation(self):
        data = deepcopy(self.test_data)
        data['urn'] = '00/aa/0000000/00'
        response1 = self._post_data(data)
        response2 = self._post_data(data)

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)

    def test_duplicate_submission_with_sent_case(self):
        data = deepcopy(self.test_data)
        data['urn'] = '00/aa/0000001/00'
        response1 = self._post_data(data)
        c = Case.objects.get(urn="00AA000000100")
        c.sent = True
        c.save()
        response2 = self._post_data(data)

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 400)

    def test_urn_blank_urn_validation(self):
        data = deepcopy(self.test_data)
        data['urn'] = ""
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)

    def test_empty_urn_validation(self):
        data = deepcopy(self.test_data)
        del data['urn']
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)

    def test_urn_invalid_format_validation(self):
        data = deepcopy(self.test_data)
        data['urn'] = "aa/00/43224234/aa/25"
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)

    def test_valid_submission(self):
        data = deepcopy(self.test_data)
        response = self._post_data(data)
        case = Case.objects.all()[0]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Case.objects.all().count(), 1)
        self.assertEqual(case.offences.all().count(), 2)
        self.assertEqual(case.urn, data["urn"])

    def test_submission_without_offence_data(self):
        data = deepcopy(self.test_data)
        data["offences"] = []
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content.decode())["non_field_errors"][0],
            "case has no offences")
        self.assertEquals(Case.objects.count(), 0)

    def test_submission_with_first_non_listed_offence_code_fails(self):
        data = deepcopy(self.test_data)
        data["offences"][0]["offence_code"] = "DF0987"
        response = self._post_data(data)

        self.assertEqual(
            response.data["non_field_errors"][0],
            ("Case 00AA0000000 contains offence codes [['DF09', 'SZ09']] "
             "not present in the whitelist"))
        self.assertEqual(response.status_code, 400)

    def test_submission_with_second_non_listed_offence_code_fails(self):
        data = deepcopy(self.test_data)
        data["offences"][1]["offence_code"] = "DF0987"
        response = self._post_data(data)

        self.assertEqual(
            json.loads(response.content.decode())["non_field_errors"][0],
            ("Case 00AA0000000 contains offence codes [['RT01', 'DF09']] not "
             "present in the whitelist"))
        self.assertEqual(response.status_code, 400)

    def test_submission_with_both_non_listed_offence_codes(self):
        data = deepcopy(self.test_data)
        data["offences"][0]["offence_code"] = "DF0987"
        data["offences"][1]["offence_code"] = "DF0988"
        response = self._post_data(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content.decode())["non_field_errors"][0],
            ("Case 00AA0000000 contains offence codes [['DF09', 'DF09']] "
             "not present in the whitelist"))

    def test_submission_with_invalid_initiation_type_fails(self):
        data = deepcopy(self.test_data)
        data["initiation_type"] = "C"
        response = self._post_data(data)
        self.assertEqual(response.status_code, 400)

    def test_valid_submissions_returns_dict_and_correct_urn(self):
        data = deepcopy(self.test_data)
        response = self._post_data(data)
        response_json = json.loads(response.content.decode())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(type(response_json), dict)
        self.assertEqual(response_json['urn'], data['urn'])

    def test_post_valid_case_creates_auditevent(self):
        data = deepcopy(self.test_data)
        data['urn'] = '00/aa/8877887/00'
        count_before = AuditEvent.objects.count()
        response = self._post_data(data)
        ae = AuditEvent.objects.filter(
            case__urn='00AA887788700').order_by(
                "-event_datetime")[0]

        self.assertEqual(AuditEvent.objects.count(), count_before + 2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ae.event_type, "case_api")
        self.assertEqual(ae.event_subtype, "success")

    def test_case_invalid_urn_creates_auditevent(self):
        data = deepcopy(self.test_data)
        data['urn'] = '0/ab/BROKEN/00'
        count_before = AuditEvent.objects.count()
        response = self._post_data(data)
        aes = AuditEvent.objects.filter(
            case=None).order_by(
                "-event_datetime")

        self.assertEqual(len(aes), count_before + 1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(aes[0].event_type, "urn_validator")
        self.assertEqual(aes[0].event_subtype, "case_invalid_invalid_urn")
