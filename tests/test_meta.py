import unittest

from azure.functions import meta


class TestMeta(unittest.TestCase):
    def test_datetime_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34.2191Z')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34.219100+00:00')

    def test_too_fractional_datetime_parse(self):
        parsed1 = self._parse_datetime('2018-12-12T03:16:34.2191989Z')
        self.assertEqual(str(parsed1), '2018-12-12 03:16:34.219198+00:00')

        parsed2 = self._parse_datetime('9999-12-31T23:59:59.9999999+00:00')
        self.assertEqual(str(parsed2), '9999-12-31 23:59:59.999999+00:00')

    def _parse_datetime(self, datetime_str):
        return meta._BaseConverter._parse_datetime(datetime_str)
