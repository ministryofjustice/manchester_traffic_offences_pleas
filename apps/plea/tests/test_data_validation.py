from django.test import TestCase
from mock import patch
from ..models import Case, Court, DataValidation
from ..views import PleaOnlineForms


class TestDataValidation(TestCase):
    def setUp(self):
        self.session = {}
        self.request_context = {}
        self.court = Court.objects.create(
            court_code="0000",
            region_code="51",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            test_mode=False)

    def test_invalid_urn_entry_doesnt_create_datavalidation_object(self):
        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "52/AA/00000/00"}, self.request_context)

        dv = DataValidation.objects.all()
        self.assertEqual(len(dv), 0)

    @patch("django.utils.translation.get_language", return_value='en')
    def test_urn_entry_creates_datavalidation_object(self, get_language):
        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "51/AA/00000/00"}, self.request_context)

        dv = DataValidation.objects.all()
        self.assertEqual(len(dv), 1)
        self.assertEqual(dv[0].urn_entered, "51/AA/00000/00")
        self.assertEqual(dv[0].urn_standardised, "51AA0000000")
        self.assertEqual(dv[0].urn_formatted, "51/AA/00000/00")
        self.assertEqual(dv[0].case_match, None)
        self.assertEqual(dv[0].case_match_count, 0)

    @patch("django.utils.translation.get_language", return_value='cy')
    def test_english_urn_entry_doesnt_create_datavalidation_object_in_welsh(self, return_value):
        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "52/AA/00000/00"}, self.request_context)

        dv = DataValidation.objects.all()
        self.assertEqual(len(dv), 0)

    @patch("django.utils.translation.get_language", return_value='en')
    def test_urn_entry_finds_case(self, get_language):
        case = Case.objects.create(urn="51AA0000000", imported=True)
        case.offences.create()

        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "51/AA/00000/00"}, self.request_context)

        dv = DataValidation.objects.all()
        self.assertEqual(len(dv), 1)
        self.assertEqual(dv[0].urn_entered, "51/AA/00000/00")
        self.assertEqual(dv[0].urn_standardised, "51AA0000000")
        self.assertEqual(dv[0].urn_formatted, "51/AA/00000/00")
        self.assertEqual(dv[0].case_match.id, case.id)
        self.assertEqual(dv[0].case_match_count, 1)

    @patch("django.utils.translation.get_language", return_value='en')
    def test_urn_entry_finds_cases(self, get_language):
        case = Case.objects.create(urn="51AA0000000", imported=True)
        case.offences.create()

        case2 = Case.objects.create(urn="51AA0000000", imported=True)
        case2.offences.create()

        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "51/AA/00000/00"}, self.request_context)

        dv = DataValidation.objects.all()
        self.assertEqual(len(dv), 1)
        self.assertEqual(dv[0].urn_entered, "51/AA/00000/00")
        self.assertEqual(dv[0].urn_standardised, "51AA0000000")
        self.assertEqual(dv[0].urn_formatted, "51/AA/00000/00")
        self.assertEqual(dv[0].case_match_count, 2)

