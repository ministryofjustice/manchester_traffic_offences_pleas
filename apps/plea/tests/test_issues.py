import redgreenunittest as unittest

from django.http.response import HttpResponseRedirect

from ..views import PleaOnlineForms
from ..models import Case

from test_plea_form import TestMultiPleaFormBase


class TestPleaFormIssues(TestMultiPleaFormBase):
    def setUp(self):
        self.session = {}
        self.request_context = {}

        self.plea_stage_pre_data_1_charge = {"case": {"date_of_hearing": "2015-01-01",
                                                      "urn_0": "06",
                                                      "urn_1": "AA",
                                                      "urn_2": "0000000",
                                                      "urn_3": "00",
                                                      "number_of_charges": 1,
                                                      "plea_made_by": "Defendant"},
                                             "your_details": {"name": "Charlie Brown",
                                                              "contact_number": "012345678",
                                                              "email": "charliebrown@example.org"}}

    def test_used_urn_in_session(self):
        case = Case.objects.create(urn="06/AA/0000000/00", name="Ian George",
                                   sent=True)
        case.save()

        self.session = {"case": {"complete": True,
                                 "date_of_hearing": "2015-01-01",
                                 "urn": "06/AA/0000000/00",
                                 "number_of_charges": 1,
                                 "plea_made_by": "Defendant"}}

        form = PleaOnlineForms(self.session, "case")
        form.save(self.plea_stage_pre_data_1_charge, self.request_context)

        result = form.render()
        self.assertIsInstance(result, HttpResponseRedirect)

