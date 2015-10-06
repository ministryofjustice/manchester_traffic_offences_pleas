from datetime import datetime

from django.test import TestCase

from make_a_plea.serializers import DateAwareSerializer


class DateAwareSerializerTests(TestCase):
    def test_serializer_dumps_plain(self):
        test_str = """{"key2": 2, "key1": "value1"}"""
        test_dict = {"key1": "value1",
                     "key2": 2}

        ds = DateAwareSerializer().dumps(test_dict)
        self.assertEqual(ds, test_str)

    def test_serializer_loads_plain(self):
        test_str = """{"key2": 2, "key1": "value1"}"""
        test_dict = {"key1": "value1",
                     "key2": 2}

        ds = DateAwareSerializer().loads(test_str)
        self.assertEqual(ds, test_dict)

    def test_serializer_dumps_datetime(self):
        test_str = """{"key2": "2014-06-03T00:00:00", "key1": "value1"}"""
        test_dict = {"key1": "value1",
                     "key2": datetime(2014, 6, 3, 0, 0)}

        ds = DateAwareSerializer().dumps(test_dict)
        self.assertEqual(ds, test_str)