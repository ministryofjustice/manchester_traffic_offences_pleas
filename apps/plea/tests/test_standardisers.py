from django.test import TestCase

from ..standardisers import *


class TestStandardisers(TestCase):

    def test_blank_standardised_urn(self):
        standardise = get_standardiser("")
        with self.assertRaises(StandardiserNoOutputException):
            standardise("")

    def test_standardise_urn(self):
        urns = {"00/AA/11111/99": "00AA1111199",
                "00/aa/11111/99": "00AA1111199",
                "0-0-aa_11111-99": "00AA1111199",
                "00aa1111199": "00AA1111199",
                # Invalid URNs should work here too:
                "aaaa-00099": "AAAA00099"}

        for urn, output in urns.items():
            self.assertEquals(output, standardise_urn(urn))

    def test_format_urn(self):
        urns = {"00AA1111199": "00/AA/11111/99",
                "00AA222222299": "00/AA/2222222/99"}

        for urn, output in urns.items():
            self.assertEquals(output, format_urn(urn))

    def test_standardise_met_urn(self):
        urns = {"02TJDS0479/15/0014AP": "02TJDS0479150014AP",
                "02TjDs0479/15/0014aP": "02TJDS0479150014AP"}

        for urn, output in urns.items():
            self.assertEquals(output, standardise_urn(urn))

    def test_format_met_urn(self):
        urns = {"02TJDS0479150014AP": "02TJDS0479/15/0014AP"}

        for urn, output in urns.items():
            self.assertEquals(output, format_met_urn(urn))
