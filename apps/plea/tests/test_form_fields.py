import unittest

from ..fields import HearingTimeField, HearingTimeWidget
from ..forms import BasePleaStepForm


class TimeForm(BasePleaStepForm):
    time_of_hearing = HearingTimeField(widget=HearingTimeWidget)


class EmailAuditTests(unittest.TestCase):
    def test_hearing_time_field_validate_ok(self):
        t = TimeForm({"time_of_hearing": "09:15"})
        self.assertTrue(t.is_valid())

    def test_hearing_time_field_validate_fail(self):
        t = TimeForm({"time_of_hearing": "09:20"})
        self.assertFalse(t.is_valid())