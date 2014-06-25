from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser

from urls import private_page


class URNRequiredTestCase(TestCase):
    urls = 'defendant.tests.urls'
    
    def test_urn_required(self):
        private_url = "/urn_required/"
        response = self.client.get(private_url)
        self.assertEqual(response.status_code, 302)

        factory = RequestFactory()
        request = factory.get(private_url)
        request.user = AnonymousUser()
        request.user.urn = "00/AA/0000000/00"
        response = private_page(request)
        self.assertEqual(response.content, "Private Page")
        self.assertEqual(response.status_code, 200)
