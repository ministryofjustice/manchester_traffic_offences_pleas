from apps.plea.tests.test_plea_form import TestMultiPleaForms
from ..models import Case, Court, StageCompletionTable
from ..views import PleaOnlineForms

class TestStageCompletion(TestMultiPleaForms):

    def setUp(self):
        super(TestStageCompletion, self).setUp()
        self.session = {}
        self.request_context = {}
        self.urn = "98AB123456"
        self.case = Case(urn=self.urn)
        self.sc_table = StageCompletionTable(case=self.case)
        self.test_session_data["case"]["urn"] = self.urn
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

        self.case.save()
        self.sc_table.save()

    def tearDown(self):
        Case.objects.filter(urn=self.urn).delete()
        StageCompletionTable.objects.filter(case=self.case).delete()

    def test_stage_completion_object_exists(self):
        form = PleaOnlineForms(self.session, "enter_urn")
        form.load(self.request_context)
        form.save({"urn": "98AB123456"}, self.request_context)
        sc = StageCompletionTable.objects.all()
        self.assertEqual(len(sc), 1)

    def test_stage_completion_updated(self):
        form = PleaOnlineForms(self.test_session_data, 'your_details')
        form.load(self.request_context)
        form.save({"first_name": "Charlie",
                "last_name": "Brown",
                "contact_number": "07802639892",
                "email": "user@example.org"}, self.request_context)
        sc = StageCompletionTable.objects.get(case=self.case)
        self.assertEqual(sc.details, True)


