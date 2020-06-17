from typing import Mapping, List
import json
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

    def test_datum_json_encode_single_level(self):
        encode = lambda d: json.dumps(d, cls=meta.DatumJsonEncoder)

        datum: meta.Datum = None
        self.assertEqual(encode(datum), "null")

        datum = meta.Datum(value=1, type=None)
        self.assertEqual(encode(datum), "null")

        datum = meta.Datum(value=b"awesome bytes", type="bytes")
        self.assertEqual(encode(datum), '"YXdlc29tZSBieXRlcw=="')

        datum = meta.Datum(value="awesome string", type="string")
        self.assertEqual(encode(datum), '"awesome string"')

        datum = meta.Datum(value=42, type="int")
        self.assertEqual(encode(datum), '42')

        datum = meta.Datum(value=43.2103, type="double")
        self.assertEqual(encode(datum), '43.2103')

    def test_datum_json_encode_collections(self):
        encode = lambda d: json.dumps(d, cls=meta.DatumJsonEncoder)

        class DatumCollectionString:
            def __init__(self, *args: List[str]):
                self.string = args
        datum = meta.Datum(value=DatumCollectionString("string 1", "string 2"),
                           type="collection_string")
        self.assertEqual(encode(datum), '["string 1", "string 2"]')

        class DatumCollectionBytes:
            def __init__(self, *args: List[bytes]):
                self.bytes = args
        datum = meta.Datum(value=DatumCollectionBytes(b"bytes 1", b"bytes 2"),
                           type="collection_bytes")
        self.assertEqual(encode(datum), '["Ynl0ZXMgMQ==", "Ynl0ZXMgMg=="]')

        class DatumCollectionSint64:
            def __init__(self, *args: List[int]):
                self.sint64 = args
        datum = meta.Datum(value=DatumCollectionSint64(1234567, 8901234),
                           type="collection_sint64")
        self.assertEqual(encode(datum), '[1234567, 8901234]')

    def test_datum_json_encode_json(self):
        encode = lambda d: json.dumps(d, cls=meta.DatumJsonEncoder)
        # String
        datum = meta.Datum(value='"string in json"',
                           type="json")
        self.assertEqual(encode(datum), '"string in json"')

        # List
        datum = meta.Datum(value='["a", "b", "c"]',
                           type="json")
        self.assertEqual(encode(datum), '["a", "b", "c"]')

        # Object
        datum = meta.Datum(value='{"name": "awesome", "value": "cool"}',
                           type="json")
        self.assertEqual(encode(datum), '{"name": "awesome", "value": "cool"}')

        # Should ignore Newlines and Spaces
        datum = meta.Datum(value='{ "name" : "awesome",\n "value":  "cool"\n}',
                           type="json")
        self.assertEqual(encode(datum), '{"name": "awesome", "value": "cool"}')

    def test_datum_json_encode_hybrid_with_python_dict(self):
        metadata_mock: Mapping[str, meta.Datum] = {}
        metadata_mock["DeliveryCount"] = meta.Datum(1, type="int")
        metadata_mock["LockToken"] = meta.Datum(
            "42c893ad-b788-46f5-bfdd-f6e3257b7d75", type="string")
        metadata_mock["sys"] = meta.Datum('''{
            "MethodName": "ServiceBusSMany"
        }''', type="json")

        # Try to serialize it into json string
        result = json.dumps(metadata_mock, cls=meta.DatumJsonEncoder)
        self.assertIsNotNone(result)

        # The deserialized_result should not have datum structure
        deserialized_result = json.loads(result)
        self.assertEqual(deserialized_result["DeliveryCount"], 1)
        self.assertEqual(deserialized_result["LockToken"],
                         "42c893ad-b788-46f5-bfdd-f6e3257b7d75")
        self.assertEqual(deserialized_result["sys"]["MethodName"],
                         "ServiceBusSMany")

    def _parse_datetime(self, datetime_str):
        return meta._BaseConverter._parse_datetime(datetime_str)
