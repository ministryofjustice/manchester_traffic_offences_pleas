import datetime
import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from ..models import Case


class TestStats(TestCase):

    def setUp(self):
        self.client = Client()
        self.create_user()

        cases = [
            {
                "urn": "06AA1970118",
                "name": "Johnny English",
                "language": "en",
                "completed_on": datetime.date(2017, 2, 22),
                "extra_data": {
                    "DOB": "1970-01-18",
                    "Surname": "English",
                    "Forename1": "Johnny",
                    "Forename2": "Adam",
                }
            },
            {
                "urn": "06AA1970119",
                "name": "Johnny English",
                "language": "en",
                "completed_on": datetime.date(2017, 4, 24),
                "extra_data": {
                    "DOB": "1970-01-19",
                    "Surname": "English",
                    "Forename1": "Johnny",
                    "Forename2": "Brent",
                }
            },
            {
                "urn": "06AA1970120",
                "name": "Cedrych Conway",
                "language": "cy",
                "completed_on": datetime.date(2017, 2, 22),
                "extra_data": {
                    "DOB": "1970-01-20",
                    "Surname": "Conway",
                    "Forename1": "Cedrych",
                    "Forename2": "Alec",
                }
            },
            {
                "urn": "06AA1970121",
                "name": "Cedrych Conway",
                "language": "cy",
                "completed_on": datetime.date(2017, 4, 24),
                "extra_data": {
                    "DOB": "1970-01-20",
                    "Surname": "Conway",
                    "Forename1": "Cedrych",
                    "Forename2": "Bryn",
                }
            },
        ]
        for case_dict in cases:
            case = Case(**case_dict)
            case.sent = True
            case.save()

    def tearDown(self):
        Case.objects.all().delete()

    def create_user(self):
        self.username = "test_staff"
        self.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=self.username)
        user.set_password(self.password)
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.save()
        self.user = user

    def test_staff_or_404(self):
        self.client.logout()
        resp_no_auth = self.client.get("/plea/stats/?language=en")
        self.client.login(username=self.username, password=self.password)
        resp_with_auth = self.client.get("/plea/stats/?language=en")

        self.assertEqual(resp_with_auth.status_code, 200)
        self.assertEqual(resp_no_auth.status_code, 404)

    def test_required_params(self):
        self.client.login(username=self.username, password=self.password)
        bad_resp = self.client.get("/plea/stats/")
        good_resp = self.client.get("/plea/stats/?language=en")

        self.assertEqual(bad_resp.status_code, 400)
        self.assertEqual(good_resp.status_code, 200)

    def test_optional_start_date(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/?language=en&end_date=3-3-2017")
        start_date = datetime.datetime(1970, 1, 1)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(  # Check default start date
            json.loads(resp.content.decode())["summary"]["start_date"],
            start_date.isoformat())

    def test_optional_end_date(self):
        self.client.login(username=self.username, password=self.password)
        now = datetime.datetime.now()
        last_day_of_last_month = now - datetime.timedelta(days=now.day)
        end_date = datetime.datetime(
            last_day_of_last_month.year,
            last_day_of_last_month.month,
            last_day_of_last_month.day,
            23, 59, 59)
        resp = self.client.get("/plea/stats/?language=en&start_date=1-1-2017")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(  # Check default end date
            json.loads(resp.content.decode())["summary"]["end_date"],
            end_date.isoformat())

    def test_start_and_end_supplied(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/?language=en&start_date=1-1-2017&end_date=31-5-2017")

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(json.loads(resp.content.decode()))  # Shouldn't be empty

    def test_content_lang_en(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/?language=en")
        example = json.loads(resp.content.decode())["latest_example"]
        summary = json.loads(resp.content.decode())["summary"]

        self.assertEqual(example["extra_data"]["Forename2"], "Brent")
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["language"], "en")
        self.assertEqual(summary["by_month"], {"February 2017": 1, "April 2017": 1})

    def test_content_lang_cy(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/?language=cy")
        summary = json.loads(resp.content.decode())["summary"]
        example = json.loads(resp.content.decode())["latest_example"]

        self.assertEqual(example["extra_data"]["Forename2"], "Bryn")
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["language"], "cy")
        self.assertEqual(summary["by_month"], {"February 2017": 1, "April 2017": 1})

    def test_start_date_filter(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/?language=en&start_date=2017-3-3")
        summary = json.loads(resp.content.decode())["summary"]

        self.assertEqual(summary["by_month"], {"April 2017": 1})

    def test_end_date_filter(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/?language=cy&end_date=2017-3-3")
        summary = json.loads(resp.content.decode())["summary"]

        self.assertEqual(summary["by_month"], {"February 2017": 1})

    def test_bad_date_fails(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/?language=cy&end_date=20173-3")

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            json.loads(resp.content.decode()),
            {"error": "Bad date format"})

    def test_missing_language(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/plea/stats/")

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            json.loads(resp.content.decode()),
            {"error": "No language given"})

"""

        "earliest_journey": "2017-03-16T17:54:37", 
        "latest_journey": "2017-03-16T17:54:09"
    }
}
"""
