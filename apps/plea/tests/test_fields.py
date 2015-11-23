from django.core.exceptions import ValidationError
from django.test import TestCase

from ..validators import is_urn_not_used
from ..models import Case


class TestUrnValidator(TestCase):

    def setUp(self):
        self.case = Case.objects.create(urn="06AA0000000", sent=True)

    def test_urn_does_not_match(self):
        self.assertTrue(is_urn_not_used("06/BB/000000/00"))

    def test_urn_matches_but_case_not_sent_or_error(self):
        self.case.sent = False
        self.case.save()

        self.assertTrue(is_urn_not_used("06/AA/00000/00"))

    def test_urn_matches(self):
        with self.assertRaises(ValidationError):
            self.assertTrue(is_urn_not_used("06/AA/00000/00"))
