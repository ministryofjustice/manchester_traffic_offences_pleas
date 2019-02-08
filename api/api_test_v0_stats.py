import datetime

from rest_framework.test import APITestCase

from apps.plea.models import Court, CourtEmailCount, UsageStats


class TestStatsAPI(APITestCase):

    def tearDown(self):
        Court.objects.all().delete()
        CourtEmailCount.objects.all().delete()
        UsageStats.objects.all().delete()

    def setUp(self):
        self.endpoint = "/v0/stats/"
        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="court@example.org",
            submission_email="court@example.org",
            enabled=True,
            test_mode=False)

        self.today = datetime.date.today()
        self.last_monday = self.today - datetime.timedelta(days=self.today.weekday())
        self.next_monday = self.last_monday + datetime.timedelta(weeks=1)

        CourtEmailCount.objects.create(
            court=self.court,
            total_pleas=1,
            total_guilty=1,
            total_not_guilty=0,
            date_sent=self.last_monday,
            hearing_date=self.next_monday,
            sent=True)

        UsageStats.objects.create(
            start_date=self.last_monday,
            online_submissions=10,
            online_guilty_pleas=9,
            online_not_guilty_pleas=3,
            postal_requisitions=5,
            postal_responses=2)

    def test_stats(self):

        response = self.client.get(
            self.endpoint,
            {},
            format="json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_stats_valid_start_date(self):

        response = self.client.get(
            self.endpoint,
            {"start": "2015-01-01"},
            format="json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_stats_incorrect_start_date(self):

        response = self.client.get(
            self.endpoint,
            {"start": "not_a_date"},
            format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(
            ("'not_a_date' value has an invalid format. It must be in "
             "YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format."),
            response.data["error"])

    def test_stats_invalid_start_date(self):

        response = self.client.get(
            self.endpoint,
            {"start": "2015-01-32"},
            format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(
            ("\'2015-01-32\' value has the correct format (YYYY-MM-DD) but it "
             "is an invalid date."),
            response.data["error"])

    def test_stats_valid_end_date(self):

        response = self.client.get(
            self.endpoint,
            {"end": "2015-01-01"},
            format="json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_stats_incorrect_end_date(self):

        response = self.client.get(
            self.endpoint,
            {"end": "not_a_date"},
            format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(
            ("'not_a_date' value has an invalid format. It must be in "
             "YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format."), response.data["error"])

    def test_stats_invalid_end_date(self):

        response = self.client.get(self.endpoint, {"end": "2015-30-32"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("\'2015-30-32\' value has the correct format (YYYY-MM-DD) but it is an invalid date.", response.data["error"])

    def test_stats_days_from_hearing(self):

        response = self.client.get("/v0/stats/days_from_hearing/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 60)

    def test_stats_by_hearing(self):

        response = self.client.get("/v0/stats/by_hearing/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, "hearing_day")
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_stats_all_by_hearing(self):

        response = self.client.get("/v0/stats/all_by_hearing/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, "hearing_day")
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_stats_by_week(self):
        CourtEmailCount.objects.create(court=self.court,
                                       total_pleas=1,
                                       total_guilty=1,
                                       total_not_guilty=0,
                                       date_sent=self.last_monday - datetime.timedelta(weeks=1),
                                       hearing_date=self.next_monday - datetime.timedelta(weeks=1),
                                       sent=True)

        response = self.client.get("/v0/stats/by_week/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, "start_date")
        self.assertContains(response, "postal_requisitions")
        self.assertContains(response, "postal_responses")
        self.assertContains(response, "online_submissions")
        self.assertContains(response, "online_guilty_pleas")
        self.assertContains(response, "online_not_guilty_pleas")

    def test_stats_by_court(self):

        response = self.client.get("/v0/stats/by_court/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, "region_code")
        self.assertContains(response, "court_name")
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_by_court_valid_start_date(self):

        response = self.client.get("/v0/stats/by_court/", {"start": "2015-01-01"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, "region_code")
        self.assertContains(response, "court_name")
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_by_court_incorrect_start_date(self):

        response = self.client.get("/v0/stats/by_court/", {"start": "not_a_date"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("'not_a_date' value has an invalid format. It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.", response.data["error"])

    def test_by_court_invalid_start_date(self):

        response = self.client.get("/v0/stats/by_court/", {"start": "2015-01-32"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("\'2015-01-32\' value has the correct format (YYYY-MM-DD) but it is an invalid date.", response.data["error"])

    def test_by_court_valid_end_date(self):

        response = self.client.get("/v0/stats/by_court/", {"end": "2015-01-01"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, "region_code")
        self.assertContains(response, "court_name")
        self.assertContains(response, "submissions")
        self.assertContains(response, "pleas")
        self.assertContains(response, "guilty")
        self.assertContains(response, "not_guilty")

    def test_by_court_incorrect_end_date(self):

        response = self.client.get("/v0/stats/by_court/", {"end": "not_a_date"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("'not_a_date' value has an invalid format. It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.", response.data["error"])

    def test_by_court_invalid_end_date(self):

        response = self.client.get("/v0/stats/by_court/", {"end": "2015-30-32"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("\'2015-30-32\' value has the correct format (YYYY-MM-DD) but it is an invalid date.", response.data["error"])

