from django.http.response import HttpResponseRedirect

from ..views import PleaOnlineForms
from ..models import Case

from test_plea_form import TestMultiPleaFormBase


class TestPleaFormIssues(TestMultiPleaFormBase):
    def setUp(self):
        self.session = {}
        self.request_context = {}

    def test_used_urn_in_session(self):
        case = Case.objects.create(urn="06AA000000000", name="Ian George",
                                   sent=True)
        case.save()

        self.session = {"notice_type": {"complete": True,
                                        "sjp": False},
                        "case": {"complete": True,
                                 "date_of_hearing": "2015-01-01",
                                 "urn": "06AA000000000",
                                 "number_of_charges": 1,
                                 "plea_made_by": "Defendant"}}

        save_data = {"date_of_hearing": "2015-01-01",
                     "urn": "06/AA/0000000/00",
                     "number_of_charges": 1,
                     "plea_made_by": "Defendant"}

        form = PleaOnlineForms(self.session, "case")
        form.save(save_data, self.request_context)

        result = form.render()
        self.assertIsInstance(result, HttpResponseRedirect)

