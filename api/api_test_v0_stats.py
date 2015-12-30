import datetime

from rest_framework.test import APITestCase

from apps.plea.models import Court, CourtEmailCount, UsageStats

class TestStatsAPI(APITestCase):

    def setUp(self):
        self.court = Court.objects.create(court_code="0000",
                                          region_code="06",
                                          court_name="test court",
                                          court_address="test address",
                                          court_telephone="0800 MAKEAPLEA",
                                          court_email="test@test.com",
                                          submission_email="test@test.com",
                                          enabled=True,
                                          test_mode=False)

        self.today = datetime.date.today()
        self.last_monday = self.today - datetime.timedelta(days=self.today.weekday())
        self.next_monday = self.last_monday + datetime.timedelta(weeks=1)

        CourtEmailCount.objects.create(court=self.court,
                                       total_pleas=1,
                                       total_guilty=1,
                                       total_not_guilty=0,
                                       date_sent=self.last_monday,
                                       hearing_date=self.next_monday,
                                       sent=True)

        UsageStats.objects.create(start_date=self.last_monday,
                                  online_submissions=10,
                                  online_guilty_pleas=9,
                                  online_not_guilty_pleas=3,
                                  postal_requisitions=5,
                                  postal_responses=2)

    def test_stats(self):

        response = self.client.get("/v0/stats/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("submissions", response.data)
        self.assertIn("pleas", response.data)
        self.assertIn("guilty", response.data)
        self.assertIn("not_guilty", response.data)

    def test_stats_valid_start_date(self):

        response = self.client.get("/v0/stats/", {"start": "2015-01-01"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("submissions", response.data)
        self.assertIn("pleas", response.data)
        self.assertIn("guilty", response.data)
        self.assertIn("not_guilty", response.data)

    def test_stats_incorrect_start_date(self):

        response = self.client.get("/v0/stats/", {"start": "not_a_date"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("'not_a_date' value has an invalid format. It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.", response.data["error"])

    def test_stats_invalid_start_date(self):

        response = self.client.get("/v0/stats/", {"start": "2015-01-32"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("\'2015-01-32\' value has the correct format (YYYY-MM-DD) but it is an invalid date.", response.data["error"])

    def test_stats_valid_end_date(self):

        response = self.client.get("/v0/stats/", {"end": "2015-01-01"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("submissions", response.data)
        self.assertIn("pleas", response.data)
        self.assertIn("guilty", response.data)
        self.assertIn("not_guilty", response.data)

    def test_stats_incorrect_end_date(self):

        response = self.client.get("/v0/stats/", {"end": "not_a_date"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual("'not_a_date' value has an invalid format. It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.", response.data["error"])

    def test_stats_invalid_end_date(self):

        response = self.client.get("/v0/stats/", {"end": "2015-30-32"}, format="json")

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
        self.assertIn("hearing_day", response.data[0])
        self.assertIn("submissions", response.data[0])
        self.assertIn("pleas", response.data[0])
        self.assertIn("guilty", response.data[0])
        self.assertIn("not_guilty", response.data[0])

    def test_stats_all_by_hearing(self):

        response = self.client.get("/v0/stats/all_by_hearing/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn("hearing_day", response.data[0])
        self.assertIn("submissions", response.data[0])
        self.assertIn("pleas", response.data[0])
        self.assertIn("guilty", response.data[0])
        self.assertIn("not_guilty", response.data[0])

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
        self.assertIn("start_date", response.data[0])
        self.assertIn("postal_requisitions", response.data[0])
        self.assertIn("postal_responses", response.data[0])
        self.assertIn("online_submissions", response.data[0])
        self.assertIn("online_guilty_pleas", response.data[0])
        self.assertIn("online_not_guilty_pleas", response.data[0])

    def test_stats_by_court(self):

        response = self.client.get("/v0/stats/by_court/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn("region_code", response.data[0])
        self.assertIn("court_name", response.data[0])
        self.assertIn("submissions", response.data[0])
        self.assertIn("pleas", response.data[0])
        self.assertIn("guilty", response.data[0])
        self.assertIn("not_guilty", response.data[0])

    def test_by_court_valid_start_date(self):

        response = self.client.get("/v0/stats/by_court/", {"start": "2015-01-01"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn("region_code", response.data[0])
        self.assertIn("court_name", response.data[0])
        self.assertIn("submissions", response.data[0])
        self.assertIn("pleas", response.data[0])
        self.assertIn("guilty", response.data[0])
        self.assertIn("not_guilty", response.data[0])

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
        self.assertIn("region_code", response.data[0])
        self.assertIn("court_name", response.data[0])
        self.assertIn("submissions", response.data[0])
        self.assertIn("pleas", response.data[0])
        self.assertIn("guilty", response.data[0])
        self.assertIn("not_guilty", response.data[0])

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

