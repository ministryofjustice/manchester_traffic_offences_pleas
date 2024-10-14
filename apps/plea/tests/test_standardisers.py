from django.test import TestCase

from ..standardisers import *


class TestStandardisers(TestCase):

    def test_blank_standardised_urn(self):
        with self.assertRaises(StandardiserNoOutputException):
            standardise_urn("")

    def test_standardise_urn(self):
        urns = {"00/AA/11111/99": "00AA1111199",
                "00/aa/11111/99": "00AA1111199",
                "0-0-aa_11111-99": "00AA1111199",
                "00aa1111199": "00AA1111199",
                # Invalid URNs should work here too:
                "aaaa-00099": "AAAA00099"}

        for urn, output in urns.items():
            self.assertEqual(output, standardise_urn(urn))

    def test_format_urn(self):
        urns = {"00AA1111199": "00/AA/11111/99",
                "00AA222222299": "00/AA/2222222/99"}

        for urn, output in urns.items():
            self.assertEqual(output, format_urn(urn))

    def test_standardise_met_urn(self):
        urns = {"02TJDS0479/15/0014AP": "02TJDS0479150014AP",
                "02TjDs0479/15/0014aP": "02TJDS0479150014AP",
                "02TJ/AA0000/00/0015aa": "02TJAA0000000015AA",
                "02TJ/AA0000/00/00151aa": "02TJAA00000000151AA",
                "02TJ/AA0000/00/00151aaa": "02TJAA00000000151AAA",
                "02TJC00000000aa": "02TJC00000000AA",
                "02TJC00000000aaa": "02TJC00000000AAA",
                "02TJ0000000000000000aa": "02TJ0000000000000000AA",
                "02TJ0000000000000000aaa": "02TJ0000000000000000AAA",
                "02TJ0000000/00aa": "02TJ000000000AA",
                "02TJ0000000/00aaa": "02TJ000000000AAA"}

        for urn, output in urns.items():
            self.assertEqual(output, standardise_urn(urn))

    def test_format_met_urn(self):
        urns = {"02TJDS0479150014AP": "02TJDS0479150014AP"}

        for urn, output in urns.items():
            self.assertEqual(output, format_met_urn(urn))
