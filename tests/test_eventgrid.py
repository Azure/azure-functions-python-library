# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime
import unittest
from typing import List

import azure.functions as func
import azure.functions.eventgrid as azf_event_grid


class MyTestCase(unittest.TestCase):
    def test_eventgrid_input_type(self):
        check_input_type = azf_event_grid.EventGridEventInConverter.\
            check_input_type_annotation
        self.assertTrue(check_input_type(func.EventGridEvent))
        self.assertFalse(check_input_type(List[func.EventGridEvent]))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))

    def test_cloudevent_input_type(self):
        check_input_type = azf_event_grid.EventGridEventInConverter.\
            check_input_type_annotation
        self.assertTrue(check_input_type(func.CloudEvent))
        self.assertFalse(check_input_type(List[func.CloudEvent]))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))

    def test_eventgrid_output_type(self):
        check_output_type = azf_event_grid.EventGridEventOutConverter.\
            check_output_type_annotation
        self.assertTrue(check_output_type(func.EventGridOutputEvent))
        self.assertTrue(check_output_type(List[func.EventGridOutputEvent]))
        self.assertTrue(check_output_type(str))
        self.assertTrue(check_output_type(bytes))
        self.assertTrue(check_output_type(List[str]))

    def test_eventgrid_decode(self):
        eventGridEvent = azf_event_grid.EventGridEventInConverter.decode(
            data=self._generate_single_eventgrid_datum(), trigger_metadata=None
        )
        self.assertEqual(
            eventGridEvent.id,
            "00010001-0001-0001-0001-000100010001")
        self.assertEqual(eventGridEvent.subject, "eventhubs/test")
        self.assertEqual(eventGridEvent.event_type, "captureFileCreated")
        self.assertEqual(eventGridEvent.topic, "/TestTopic/namespaces/test")
        self.assertIsNotNone(eventGridEvent.get_json())

    def test_eventgrid_decode_with_null_data(self):
        eventGridEvent = azf_event_grid.EventGridEventInConverter.decode(
            data=self._generate_single_eventgrid_datum(
                with_data=False), trigger_metadata=None)
        self.assertEqual(
            eventGridEvent.id,
            "00010001-0001-0001-0001-000100010001")
        self.assertEqual(eventGridEvent.subject, "eventhubs/test")
        self.assertEqual(eventGridEvent.event_type, "captureFileCreated")
        self.assertEqual(eventGridEvent.topic, "/TestTopic/namespaces/test")
        self.assertIsNone(eventGridEvent.get_json())

    def test_eventgrid_encode_with_str_data(self):
        example_data = self._generate_single_eventgrid_str()
        eventGridDatum = azf_event_grid.EventGridEventOutConverter.encode(
            example_data, expected_type=type(example_data))
        self.assertEqual(eventGridDatum.type, "string")

    def test_eventgrid_encode_with_bytes_data(self):
        example_data = self._generate_single_eventgrid_str(True)
        eventGridDatum = azf_event_grid.EventGridEventOutConverter.encode(
            example_data, expected_type=type(example_data))
        self.assertEqual(eventGridDatum.type, "bytes")

    def test_eventgrid_encode_with_EventGridData(self):
        example_data = self._generate_single_eventgrid_event()
        event_grid_datum = azf_event_grid.EventGridEventOutConverter.encode(
            example_data, expected_type=type(example_data))

        self.assertEqual(event_grid_datum.type, "json")

    def test_eventgrid_encode_with_multiple_EventGridData(self):
        example_data = self._generate_multiple_eventgrid_event()
        event_grid_datum = azf_event_grid.EventGridEventOutConverter.encode(
            example_data, expected_type=type(example_data))

        self.assertEqual(event_grid_datum.type, "json")

    @staticmethod
    def _generate_single_eventgrid_datum(with_data=True, datum_type='json'):
        datum_with_data = """
{
  "topic": "/TestTopic/namespaces/test",
  "subject": "eventhubs/test",
  "eventType": "captureFileCreated",
  "eventTime": "2017-07-14T23:10:27.7689666Z",
  "id": "00010001-0001-0001-0001-000100010001",
  "data": {
    "fileUrl": "https://test.blob.core.windows.net/debugging/testblob.txt",
    "fileType": "AzureBlockBlob",
    "partitionId": "1",
    "sizeInBytes": 0,
    "eventCount": 0,
    "firstSequenceNumber": -1,
    "lastSequenceNumber": -1,
    "firstEnqueueTime": "0001-01-01T00:00:00",
    "lastEnqueueTime": "0001-01-01T00:00:00"
  },
  "dataVersion": "",
  "metadataVersion": "1"
}
"""
        datum_without_data = """
{
  "topic": "/TestTopic/namespaces/test",
  "subject": "eventhubs/test",
  "eventType": "captureFileCreated",
  "eventTime": "2017-07-14T23:10:27.7689666Z",
  "id": "00010001-0001-0001-0001-000100010001",
  "dataVersion": "",
  "metadataVersion": "1"
}"""

        datum = datum_with_data if with_data else datum_without_data

        if datum_type == 'bytes':
            datum = datum.encode('utf-8')

        return func.meta.Datum(datum, datum_type)

    @staticmethod
    def _generate_single_eventgrid_event(with_date=True):
        return azf_event_grid.azf_eventgrid.EventGridOutputEvent(
            id="id",
            subject='subject',
            event_type='eventType',
            event_time=datetime.utcnow(),
            data={"tag1": "value1", "tag2": "value2"} if with_date else {},
            data_version='dataVersion',
        )

    @staticmethod
    def _generate_multiple_eventgrid_event(with_date=True):
        return [azf_event_grid.azf_eventgrid.EventGridOutputEvent(
            id="id1",
            subject='subject1',
            event_type='eventType1',
            event_time=datetime.utcnow(),
            data={"tag1": "value1", "tag2": "value2"} if with_date else {},
            data_version='dataVersion',
        ), azf_event_grid.azf_eventgrid.EventGridOutputEvent(
            id="id2",
            subject='subject2',
            event_type='eventType2',
            event_time=datetime.utcnow(),
            data={"tag1": "value1", "tag2": "value2"} if with_date else {},
            data_version='dataVersion',
        )]

    def test_cloudevent_decode(self):
        event = azf_event_grid.EventGridEventInConverter.decode(
            data=self._generate_single_cloudevent_datum(), trigger_metadata=None
        )
        self.assertIsInstance(event, azf_event_grid.azf_eventgrid.CloudEvent)
        self.assertEqual(event.id, "A234-1234-1234")
        self.assertEqual(event.source, "/mycontext/subcontext")
        self.assertEqual(event.type, "com.example.type")
        self.assertEqual(event.specversion, "1.0")
        self.assertEqual(event.subject, "mysubject")
        self.assertEqual(event.datacontenttype, "application/json")
        self.assertIsNotNone(event.time)
        self.assertIsNotNone(event.get_json())
        self.assertEqual(event.get_json().get("key"), "value")

    def test_cloudevent_decode_with_null_data(self):
        event = azf_event_grid.EventGridEventInConverter.decode(
            data=self._generate_single_cloudevent_datum(with_data=False),
            trigger_metadata=None
        )
        self.assertIsInstance(event, azf_event_grid.azf_eventgrid.CloudEvent)
        self.assertEqual(event.id, "A234-1234-1234")
        self.assertIsNone(event.get_json())

    def test_cloudevent_decode_with_extensions(self):
        event = azf_event_grid.EventGridEventInConverter.decode(
            data=self._generate_single_cloudevent_datum(with_extensions=True),
            trigger_metadata=None
        )
        self.assertIsInstance(event, azf_event_grid.azf_eventgrid.CloudEvent)
        self.assertEqual(event.extension_attrs.get("customext"), "extvalue")

    def test_eventgrid_schema_not_broken(self):
        event = azf_event_grid.EventGridEventInConverter.decode(
            data=self._generate_single_eventgrid_datum(), trigger_metadata=None
        )
        self.assertIsInstance(event, azf_event_grid.azf_eventgrid.EventGridEvent)
        self.assertEqual(event.id, "00010001-0001-0001-0001-000100010001")
        self.assertEqual(event.topic, "/TestTopic/namespaces/test")
        self.assertEqual(event.event_type, "captureFileCreated")

    @staticmethod
    def _generate_single_cloudevent_datum(with_data=True,
                                          with_extensions=False):
        payload = {
            "specversion": "1.0",
            "type": "com.example.type",
            "source": "/mycontext/subcontext",
            "id": "A234-1234-1234",
            "time": "2018-04-05T17:31:00Z",
            "subject": "mysubject",
            "datacontenttype": "application/json",
        }
        if with_data:
            payload["data"] = {"key": "value"}
        if with_extensions:
            payload["customext"] = "extvalue"
        import json as _json
        return func.meta.Datum(_json.dumps(payload), 'json')

    @staticmethod
    def _generate_single_eventgrid_str(in_bytes=False):
        string_representation = '{"id": "id", ' \
                                '"subject": "subject", ' \
                                '"dataVersion": "dataVersion", ' \
                                '"eventType": "eventType", ' \
                                '"data": {"tag1": "value1", ' \
                                '"tag2": "value2"}, ' \
                                '"eventTime": "2020-04-22T18:19:19Z"}'
        return string_representation.encode('utf-8') \
            if in_bytes \
            else string_representation


if __name__ == '__main__':
    unittest.main()
