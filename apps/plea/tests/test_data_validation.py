from django.test import TestCase

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
            court_email="test@test.com",
            submission_email=True,
            plp_email="test@test.com",
            enabled=True,
            test_mode=False)

    def test_invalid_urn_entry_doesnt_create_datavalidation_object(self):
        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "52/AA/00000/00"}, self.request_context)

        dv = DataValidation.objects.all()
        self.assertEqual(len(dv), 0)

    def test_urn_entry_creates_datavalidation_object(self):
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

    def test_urn_entry_finds_case(self):
        case = Case.objects.create(urn="51AA0000000")
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

    def test_urn_entry_finds_cases(self):
        case = Case.objects.create(urn="51AA0000000")
        case.offences.create()

        case2 = Case.objects.create(urn="51AA0000000")
        case2.offences.create()

        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "51/AA/00000/00"}, self.request_context)

        dv = DataValidation.objects.all()
        self.assertEqual(len(dv), 1)
        self.assertEqual(dv[0].urn_entered, "51/AA/00000/00")
        self.assertEqual(dv[0].urn_standardised, "51AA0000000")
        self.assertEqual(dv[0].urn_formatted, "51/AA/00000/00")
        self.assertEqual(dv[0].case_match.id, case2.id)
        self.assertEqual(dv[0].case_match_count, 2)
