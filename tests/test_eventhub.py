from typing import List
import unittest
import json
from unittest.mock import patch
from datetime import datetime

import azure.functions as func
import azure.functions.eventhub as azf_eh
import azure.functions.meta as meta


class CollectionBytes:
    def __init__(self, data: List[bytes]):
        self.bytes = data


class CollectionString:
    def __init__(self, data: List[str]):
        self.string = list(map(lambda x: x.encode('utf-8'), data))


class TestEventHub(unittest.TestCase):
    MOCKED_ENQUEUE_TIME = datetime.utcnow()

    def test_eventhub_input_type(self):
        check_input_type = (
            azf_eh.EventHubConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(func.EventHubEvent))
        self.assertTrue(check_input_type(List[func.EventHubEvent]))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))
        self.assertFalse(check_input_type(List[str]))

    def test_eventhub_output_type(self):
        check_output_type = (
            azf_eh.EventHubTriggerConverter.check_output_type_annotation
        )
        self.assertTrue(check_output_type(bytes))
        self.assertTrue(check_output_type(str))
        self.assertTrue(check_output_type(List[str]))
        self.assertFalse(check_output_type(func.EventHubEvent))
        self.assertFalse(check_output_type(List[bytes]))
        self.assertFalse(check_output_type(List[func.EventHubEvent]))

    @patch('azure.functions.eventhub.EventHubTriggerConverter'
           '.decode_single_event')
    @patch('azure.functions.eventhub.EventHubTriggerConverter'
           '.decode_multiple_events')
    def test_eventhub_decode_single_event(self, dme_mock, dse_mock):
        azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_single_iothub_datum(),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        dse_mock.assert_called_once()
        dme_mock.assert_not_called()

    @patch('azure.functions.eventhub.EventHubTriggerConverter'
           '.decode_single_event')
    @patch('azure.functions.eventhub.EventHubTriggerConverter'
           '.decode_multiple_events')
    def test_eventhub_decode_multiple_events(self, dme_mock, dse_mock):
        azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_multiple_iothub_data(),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        dse_mock.assert_not_called()
        dme_mock.assert_called_once()

    def test_eventhub_trigger_single_event_json(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_single_iothub_datum('json'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        # Result body always has the datatype of bytes
        self.assertEqual(
            result.get_body().decode('utf-8'), '{"device-status": "good"}'
        )
        self.assertEqual(result.enqueued_time, self.MOCKED_ENQUEUE_TIME)

    def test_eventhub_trigger_single_event_bytes(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_single_iothub_datum('bytes'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        self.assertEqual(
            result.get_body().decode('utf-8'), '{"device-status": "good"}'
        )
        self.assertEqual(result.enqueued_time, self.MOCKED_ENQUEUE_TIME)

    def test_iothub_metadata_single_event(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_single_iothub_datum('json'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        self.assertIsNotNone(result.iothub_metadata)
        self.assertEqual(
            result.iothub_metadata['connection-device-id'], 'MyTestDevice'
        )

    def test_eventhub_trigger_single_event_string(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_single_iothub_datum('string'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        self.assertEqual(
            result.get_body().decode('utf-8'), '{"device-status": "good"}'
        )
        self.assertEqual(result.enqueued_time, self.MOCKED_ENQUEUE_TIME)

    def test_eventhub_trigger_multiple_events_json(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_multiple_iothub_data('json'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].enqueued_time, self.MOCKED_ENQUEUE_TIME)
        self.assertEqual(
            result[0].get_body().decode('utf-8'), '{"device-status": "good1"}'
        )

        self.assertEqual(result[1].enqueued_time, self.MOCKED_ENQUEUE_TIME)
        self.assertEqual(
            result[1].get_body().decode('utf-8'), '{"device-status": "good2"}'
        )

    def test_eventhub_trigger_multiple_events_collection_string(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_multiple_iothub_data('collection_string'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].enqueued_time, self.MOCKED_ENQUEUE_TIME)
        self.assertEqual(
            result[0].get_body().decode('utf-8'), '{"device-status": "good1"}'
        )

        self.assertEqual(result[1].enqueued_time, self.MOCKED_ENQUEUE_TIME)
        self.assertEqual(
            result[1].get_body().decode('utf-8'), '{"device-status": "good2"}'
        )

    def test_eventhub_trigger_multiple_events_collection_bytes(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_multiple_iothub_data('collection_bytes'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].enqueued_time, self.MOCKED_ENQUEUE_TIME)
        self.assertEqual(
            result[0].get_body().decode('utf-8'), '{"device-status": "good1"}'
        )

        self.assertEqual(result[1].enqueued_time, self.MOCKED_ENQUEUE_TIME)
        self.assertEqual(
            result[1].get_body().decode('utf-8'), '{"device-status": "good2"}'
        )

    def test_iothub_metadata_events(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_multiple_iothub_data('json'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsNotNone(result[0].iothub_metadata)
        self.assertEqual(
            result[0].iothub_metadata['connection-device-id'], 'MyTestDevice1'
        )

        self.assertIsNotNone(result[1].iothub_metadata)
        self.assertEqual(
            result[1].iothub_metadata['connection-device-id'], 'MyTestDevice2'
        )

    def _generate_single_iothub_datum(self, datum_type='json'):
        datum = '{"device-status": "good"}'
        if datum_type == 'bytes':
            datum = datum.encode('utf-8')

        return meta.Datum(datum, datum_type)

    def _generate_multiple_iothub_data(self, data_type='json'):
        data = '[{"device-status": "good1"}, {"device-status": "good2"}]'
        if data_type == 'collection_bytes':
            data = list(
                map(lambda x: json.dumps(x).encode('utf-8'), json.loads(data))
            )
            data = CollectionBytes(data)
        elif data_type == 'collection_string':
            data = list(
                map(lambda x: json.dumps(x), json.loads(data))
            )
            data = CollectionString(data)

        return meta.Datum(data, data_type)

    def _generate_single_trigger_metadatum(self):
        return {
            'EnqueuedTime': meta.Datum(
                f'"{self.MOCKED_ENQUEUE_TIME.isoformat()}"', 'json'
            ),
            'SystemProperties': meta.Datum(
                '{"iothub-connection-device-id": "MyTestDevice"}', 'json'
            )
        }

    def _generate_multiple_trigger_metadata(self):
        system_props_array = [
            {
                'EnqueuedTimeUtc': self.MOCKED_ENQUEUE_TIME.isoformat(),
                'iothub-connection-device-id': 'MyTestDevice1',
            },
            {
                'EnqueuedTimeUtc': self.MOCKED_ENQUEUE_TIME.isoformat(),
                'iothub-connection-device-id': 'MyTestDevice2',
            }
        ]

        return {
            'SystemPropertiesArray': meta.Datum(
                json.dumps(system_props_array), 'json'
            )
        }
