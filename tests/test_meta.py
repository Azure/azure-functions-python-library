import unittest
import datetime

from azure.functions import meta


class TestMeta(unittest.TestCase):
    def test_utc_datetime_no_fraction_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34Z')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34+00:00')
        self.assertEqual(parsed.tzinfo, datetime.timezone.utc)

    def test_utc_datetime_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34.2191Z')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34.219100+00:00')

    def test_utc_datetime_neg_tz_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34.2191-00:00')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34.219100+00:00')

    def test_too_fractional_utc_datetime_parse(self):
        parsed1 = self._parse_datetime('2018-12-12T03:16:34.2191989Z')
        self.assertEqual(str(parsed1), '2018-12-12 03:16:34.219198+00:00')

        parsed2 = self._parse_datetime('9999-12-31T23:59:59.9999999+00:00')
        self.assertEqual(str(parsed2), '9999-12-31 23:59:59.999999+00:00')

    def test_local_datetime_no_fraction_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34')

    def test_local_datetime_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34.2191')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34.219100')

    def test_too_fractional_local_datetime_parse(self):
        parsed1 = self._parse_datetime('2018-08-07T23:17:57.4610506')
        self.assertEqual(str(parsed1), '2018-08-07 23:17:57.461050')

        parsed2 = self._parse_datetime('9999-12-31T23:59:59.9999999')
        self.assertEqual(str(parsed2), '9999-12-31 23:59:59.999999')

    def test_parse_utc_datetime_failure(self):
        malformed_utc = '2018-12-12X03:16:34.219289Z'
        with self.assertRaises(ValueError) as context:
            self._parse_datetime(malformed_utc)

        self.assertIn(malformed_utc, str(context.exception))

    def test_parse_local_datetime_failure(self):
        malformed_local = '2018-12-12X03:16:34.219289'
        with self.assertRaises(ValueError) as context:
            self._parse_datetime(malformed_local)

        self.assertIn(malformed_local, str(context.exception))

    def _parse_datetime(self, datetime_str):
        return meta._BaseConverter._parse_datetime(datetime_str)
