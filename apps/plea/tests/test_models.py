from __future__ import absolute_import, unicode_literals
import datetime as dt 
import unittest

from ..models import CourtEmailCount


class CourtEmailCountModelTestCase(unittest.TestCase):

    def test_get_from_context_hearing_date_is_combined_date_and_time(self):
        context = {
            "plea": {
                "PleaForms": {},
            },
            "your_details": {},
            "case": {
                "date_of_hearing": "2014-09-22",
                "time_of_hearing": "09:15:00"
            }
        }

        emailcount = CourtEmailCount()
        emailcount.get_from_context(context)

        self.assertEquals(emailcount.hearing_date, dt.datetime(2014, 9, 22, 9, 15, 0))

