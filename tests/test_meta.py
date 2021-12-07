# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Mapping, List
import unittest
import datetime

from azure.functions import meta


class TestMeta(unittest.TestCase):
    def test_parsed_datetime_none(self):
        parsed = self._parse_datetime(None)
        self.assertEqual(parsed, None)

    def test_parse_datetime_empty(self):
        parsed = self._parse_datetime('')
        self.assertEqual(parsed, None)

    def test_utc_datetime_no_fraction_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34Z')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34+00:00')
        self.assertEqual(parsed.tzinfo, datetime.timezone.utc)

        parsed = self._parse_datetime('12/31/9999 23:59:59Z')
        self.assertEqual(str(parsed), '9999-12-31 23:59:59+00:00')
        self.assertEqual(parsed.tzinfo, datetime.timezone.utc)

    def test_utc_datetime_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34.2191Z')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34.219100+00:00')

        parsed = self._parse_datetime('12/31/9999 23:59:59.000000Z')
        self.assertEqual(str(parsed), '9999-12-31 23:59:59+00:00')

        parsed = self._parse_datetime('12/31/9999 23:59:59.999999Z')
        self.assertEqual(str(parsed), '9999-12-31 23:59:59.999999+00:00')

    def test_utc_datetime_neg_tz_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34.2191-00:00')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34.219100+00:00')

        parsed = self._parse_datetime('12/31/9999 23:59:59.999999-00:00')
        self.assertEqual(str(parsed), '9999-12-31 23:59:59.999999+00:00')

    def test_too_fractional_utc_datetime_parse(self):
        parsed1 = self._parse_datetime('2018-12-12T03:16:34.2191989Z')
        self.assertEqual(str(parsed1), '2018-12-12 03:16:34.219198+00:00')

        parsed2 = self._parse_datetime('9999-12-31T23:59:59.9999999+00:00')
        self.assertEqual(str(parsed2), '9999-12-31 23:59:59.999999+00:00')

        parsed3 = self._parse_datetime('12/31/9999 23:59:59.9999999Z')
        self.assertEqual(str(parsed3), '9999-12-31 23:59:59.999999+00:00')

        parsed4 = self._parse_datetime('12/31/9999 23:59:59.9999999+00:00')
        self.assertEqual(str(parsed4), '9999-12-31 23:59:59.999999+00:00')

    def test_local_datetime_no_fraction_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34')

        parsed2 = self._parse_datetime('12/31/9999T23:59:59')
        self.assertEqual(str(parsed2), '9999-12-31 23:59:59')

    def test_local_datetime_parse(self):
        parsed = self._parse_datetime('2018-12-12T03:16:34.2191')
        self.assertEqual(str(parsed), '2018-12-12 03:16:34.219100')

        parsed2 = self._parse_datetime('12/31/9999T23:59:59.219100')
        self.assertEqual(str(parsed2), '9999-12-31 23:59:59.219100')

    def test_too_fractional_local_datetime_parse(self):
        parsed1 = self._parse_datetime('2018-08-07T23:17:57.4610506')
        self.assertEqual(str(parsed1), '2018-08-07 23:17:57.461050')

        parsed2 = self._parse_datetime('9999-12-31T23:59:59.9999999')
        self.assertEqual(str(parsed2), '9999-12-31 23:59:59.999999')

        parsed3 = self._parse_datetime('12/31/9999T23:59:59.9999999')
        self.assertEqual(str(parsed3), '9999-12-31 23:59:59.999999')

    def test_parsed_timedelta_none(self):
        parsed = self._parse_timedelta(None)
        self.assertIsNone(parsed)

    def test_parsed_timedelta_empty(self):
        parsed = self._parse_timedelta('')
        self.assertIsNone(parsed)

    def test_parse_timedelta_seconds(self):
        # Zeros
        parsed = self._parse_timedelta('0')
        self.assertEqual(parsed.seconds, 0)

        # Single Digit
        parsed = self._parse_timedelta('3')
        self.assertEqual(parsed.seconds, 3)

        # Double Digit
        parsed = self._parse_timedelta('56')
        self.assertEqual(parsed.seconds, 56)

        parsed = self._parse_timedelta('678')
        self.assertEqual(parsed.seconds, 678)

    def test_parse_timedelta_minutes_seconds(self):
        # Single Digits Zeros
        parsed = self._parse_timedelta('0:0')
        self.assertEqual(parsed.seconds, 0)

        # Single Digits
        parsed = self._parse_timedelta('3:4')
        self.assertEqual(parsed.seconds, 3 * 60 + 4)

        # Double Digits Zeros
        parsed = self._parse_timedelta('00:00')
        self.assertEqual(parsed.seconds, 0)

        # Double Digits
        parsed = self._parse_timedelta('34:56')
        self.assertEqual(parsed.seconds, 34 * 60 + 56)

    def test_parse_timedelta_hours_minutes_seconds(self):
        # Single Digits Zeros
        parsed = self._parse_timedelta('0:0:0')
        self.assertEqual(parsed.seconds, 0)

        # Single Digits
        parsed = self._parse_timedelta('3:4:5')
        self.assertEqual(parsed.seconds, 3 * 3600 + 4 * 60 + 5)

        # Double Digits Zeros
        parsed = self._parse_timedelta('00:00:00')
        self.assertEqual(parsed.seconds, 0)

        # Double Digits
        parsed = self._parse_timedelta('12:34:56')
        self.assertEqual(parsed.seconds, 12 * 3600 + 34 * 60 + 56)

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

    def test_datum_single_level_python_value(self):
        datum: Mapping[str, meta.Datum] = meta.Datum(value=None, type="int")
        self.assertEqual(datum.python_value, None)
        self.assertEqual(datum.python_type, type(None))

        datum = meta.Datum(value=1, type=None)
        self.assertEqual(datum.python_value, None)
        self.assertEqual(datum.python_type, type(None))

        datum = meta.Datum(value=b"awesome bytes", type="bytes")
        self.assertEqual(datum.python_value, b"awesome bytes")
        self.assertEqual(datum.python_type, bytes)

        datum = meta.Datum(value="awesome string", type="string")
        self.assertEqual(datum.python_value, 'awesome string')
        self.assertEqual(datum.python_type, str)

        datum = meta.Datum(value=42, type="int")
        self.assertEqual(datum.python_value, 42)
        self.assertEqual(datum.python_type, int)

        datum = meta.Datum(value=43.2103, type="double")
        self.assertEqual(datum.python_value, 43.2103)
        self.assertEqual(datum.python_type, float)

    def test_datum_collections_python_value(self):
        class DatumCollectionString:
            def __init__(self, *args: List[str]):
                self.string = args
        datum = meta.Datum(value=DatumCollectionString("string 1", "string 2"),
                           type="collection_string")
        self.assertListEqual(datum.python_value, ["string 1", "string 2"])
        self.assertEqual(datum.python_type, list)

        class DatumCollectionBytes:
            def __init__(self, *args: List[bytes]):
                self.bytes = args
        datum = meta.Datum(value=DatumCollectionBytes(b"bytes 1", b"bytes 2"),
                           type="collection_bytes")
        self.assertListEqual(datum.python_value, [b"bytes 1", b"bytes 2"])
        self.assertEqual(datum.python_type, list)

        class DatumCollectionSint64:
            def __init__(self, *args: List[int]):
                self.sint64 = args
        datum = meta.Datum(value=DatumCollectionSint64(1234567, 8901234),
                           type="collection_sint64")
        self.assertListEqual(datum.python_value, [1234567, 8901234])
        self.assertEqual(datum.python_type, list)

    def test_datum_json_python_value(self):
        # None
        datum = meta.Datum(value='null',
                           type="json")
        self.assertEqual(datum.python_value, None)
        self.assertEqual(datum.python_type, type(None))

        # Int
        datum = meta.Datum(value='123',
                           type="json")
        self.assertEqual(datum.python_value, 123)
        self.assertEqual(datum.python_type, int)

        # Float
        datum = meta.Datum(value='456.789',
                           type="json")
        self.assertEqual(datum.python_value, 456.789)
        self.assertEqual(datum.python_type, float)

        # String
        datum = meta.Datum(value='"string in json"',
                           type="json")
        self.assertEqual(datum.python_value, "string in json")
        self.assertEqual(datum.python_type, str)

        # List
        datum = meta.Datum(value='["a", "b", "c"]',
                           type="json")
        self.assertListEqual(datum.python_value, ["a", "b", "c"])
        self.assertEqual(datum.python_type, list)

        # Object
        datum = meta.Datum(value='{"name": "awesome", "value": "cool"}',
                           type="json")
        self.assertDictEqual(datum.python_value, {
            "name": "awesome",
            "value": "cool"})
        self.assertEqual(datum.python_type, dict)

        # Should ignore Newlines and Spaces
        datum = meta.Datum(value='{ "name" : "awesome",\n "value":  "cool"\n}',
                           type="json")
        self.assertDictEqual(datum.python_value, {
            "name": "awesome",
            "value": "cool"})
        self.assertEqual(datum.python_type, dict)

    def _parse_datetime(self, datetime_str):
        return meta._BaseConverter._parse_datetime(datetime_str)

    def _parse_timedelta(self, timedelta_str):
        return meta._BaseConverter._parse_timedelta(timedelta_str)
