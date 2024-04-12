# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List, Mapping
import unittest
import json
from unittest.mock import patch
from datetime import datetime

import azure.functions as func
import azure.functions.eventhub as azf_eh
import azure.functions.meta as meta

from tests.utils.testutils import CollectionBytes, CollectionString


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

    def test_single_eventhub_trigger_metadata_field(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_single_iothub_datum(),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )

        # Ensure the event enqueue_time property reflects the sys prop
        self.assertEqual(result.enqueued_time, self.MOCKED_ENQUEUE_TIME)

        # System Properties should be propagated in metadata
        metadata_dict = result.metadata
        self.assertIsNotNone(metadata_dict.get('SystemProperties'))

        # EnqueuedTime should be in iso8601 string format
        self.assertEqual(metadata_dict['EnqueuedTimeUtc'],
                         self.MOCKED_ENQUEUE_TIME.isoformat())
        self.assertEqual(metadata_dict['SystemProperties'][
            'iothub-connection-device-id'
        ], 'MyTestDevice')

    def test_multiple_eventhub_triggers_metadata_field(self):
        result = azf_eh.EventHubTriggerConverter.decode(
            data=self._generate_multiple_iothub_data(),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )

        # Any of the event should contain the full metadata
        event = result[0]
        metadata_dict = event.metadata
        self.assertIsNotNone(metadata_dict)

        # Ensure the event enqueue_time property reflects the sys prop
        self.assertEqual(event.enqueued_time, self.MOCKED_ENQUEUE_TIME)

        # Multiple metadata should be reflected in the list
        self.assertIsNotNone(metadata_dict.get('SystemPropertiesArray'))

        # EnqueuedTimeUtc should be in iso8601 string format
        self.assertEqual(metadata_dict['SystemPropertiesArray'][0][
            'EnqueuedTimeUtc'], self.MOCKED_ENQUEUE_TIME.isoformat())
        self.assertEqual(metadata_dict['SystemPropertiesArray'][0][
            'iothub-connection-device-id'
        ], 'MyTestDevice1')

    def test_eventhub_properties(self):
        """Test if properties from public interface _eventhub.py returns
        the correct values from metadata"""

        result = azf_eh.EventHubTriggerConverter.decode(
            data=meta.Datum(b'body_bytes', 'bytes'),
            trigger_metadata=self._generate_full_metadata()
        )

        self.assertEqual(result.get_body(), b'body_bytes')
        self.assertIsNone(result.partition_key)
        self.assertDictEqual(result.iothub_metadata,
                             {'connection-device-id': 'awesome-device-id'})
        self.assertEqual(result.sequence_number, 47)
        self.assertEqual(result.enqueued_time.isoformat(),
                         '2020-07-14T01:27:55.627000+00:00')
        self.assertEqual(result.offset, '3696')

    @patch('azure.functions.eventhub.EventHubConverter'
           '.decode_single_event')
    @patch('azure.functions.eventhub.EventHubConverter'
           '.decode_multiple_events')
    def test_eventhub_decode_call_single_event(self, dme_mock, dse_mock):
        azf_eh.EventHubConverter.decode(
            data=self._generate_single_iothub_datum(),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        dse_mock.assert_called_once()
        dme_mock.assert_not_called()

    @patch('azure.functions.eventhub.EventHubConverter'
           '.decode_single_event')
    @patch('azure.functions.eventhub.EventHubConverter'
           '.decode_multiple_events')
    def test_eventhub_decode_call_multiple_events(self, dme_mock, dse_mock):
        azf_eh.EventHubConverter.decode(
            data=self._generate_multiple_iothub_data(
                data_type='collection_bytes'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        dse_mock.assert_not_called()
        dme_mock.assert_called_once()

    def test_eventhub_single_event_json(self):
        result = azf_eh.EventHubConverter.decode(
            data=self._generate_single_iothub_datum('json'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        # Result body always has the datatype of bytes
        self.assertEqual(
            result.get_body().decode('utf-8'), '{"device-status": "good"}'
        )

    def test_eventhub_single_event_bytes(self):
        result = azf_eh.EventHubConverter.decode(
            data=self._generate_single_iothub_datum('bytes'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        self.assertEqual(
            result.get_body().decode('utf-8'), '{"device-status": "good"}'
        )

    def test_eventhub_multiple_events_collection_bytes(self):
        result = azf_eh.EventHubConverter.decode(
            data=self._generate_multiple_iothub_data('collection_bytes'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0].get_body().decode('utf-8'), '{"device-status": "good1"}'
        )

        self.assertEqual(
            result[1].get_body().decode('utf-8'), '{"device-status": "good2"}'
        )

    def test_eventhub_multiple_events_collection_string(self):
        result = azf_eh.EventHubConverter.decode(
            data=self._generate_multiple_iothub_data('collection_string'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0].get_body(), '{"device-status": "good1"}'
        )

        self.assertEqual(
            result[1].get_body(), '{"device-status": "good2"}'
        )

    def test_eventhub_encode_string(self):
        result = azf_eh.EventHubConverter.encode(obj="dummy_string",
                                                 expected_type=None)

        self.assertEqual(result.type, "string")
        self.assertEqual(result.value, "dummy_string")

    def test_eventhub_encode_bytes(self):
        result = azf_eh.EventHubConverter.encode(obj=b"dummy_bytes",
                                                 expected_type=None)

        self.assertEqual(result.type, "bytes")
        self.assertEqual(result.value, b"dummy_bytes")

    def test_eventhub_encode_int(self):
        result = azf_eh.EventHubConverter.encode(obj=1,
                                                 expected_type=None)

        self.assertEqual(result.type, "int")
        self.assertEqual(result.value, 1)

    def test_eventhub_encode_json(self):
        data = ["dummy_val1", "dummy_val2"]
        result = azf_eh.EventHubConverter.encode(obj=data,
                                                 expected_type=None)

        self.assertEqual(result.type, "json")
        self.assertEqual(result.value, json.dumps(data))

    def _generate_full_metadata(self):
        mocked_metadata: Mapping[str, meta.Datum] = {}
        mocked_metadata['Offset'] = meta.Datum(type='string', value='3696')
        mocked_metadata['EnqueuedTimeUtc'] = meta.Datum(
            type='string', value='2020-07-14T01:27:55.627Z')
        mocked_metadata['SequenceNumber'] = meta.Datum(type='int', value=47)
        mocked_metadata['Properties'] = meta.Datum(type='json', value='{}')
        mocked_metadata['sys'] = meta.Datum(type='json', value='''
        {
            "MethodName":"metadata_trigger",
            "UtcNow":"2020-07-14T01:27:55.8940305Z",
            "RandGuid":"db413fd6-8411-4e51-844c-c9b5345e537d"
        }''')
        mocked_metadata['SystemProperties'] = meta.Datum(type='json', value='''
        {
            "x-opt-sequence-number":47,
            "x-opt-offset":"3696",
            "x-opt-enqueued-time":"2020-07-14T01:27:55.627Z",
            "SequenceNumber":47,
            "Offset":"3696",
            "PartitionKey":null,
            "EnqueuedTimeUtc":"2020-07-14T01:27:55.627Z",
            "iothub-connection-device-id":"awesome-device-id"
        }''')
        mocked_metadata['PartitionContext'] = meta.Datum(type='json', value='''
        {
            "CancellationToken":{
            "IsCancellationRequested":false,
            "CanBeCanceled":true,
            "WaitHandle":{
                "Handle":{
                    "value":2472
                },
                "SafeWaitHandle":{
                    "IsInvalid":false,
                    "IsClosed":false
                }
            }
            },
            "ConsumerGroupName":"$Default",
            "EventHubPath":"python-worker-ci-eventhub-one-metadata",
            "PartitionId":"0",
            "Owner":"88cec2e2-94c9-4e08-acb6-4f2b97cd888e",
            "RuntimeInformation":{
            "PartitionId":"0",
            "LastSequenceNumber":0,
            "LastEnqueuedTimeUtc":"0001-01-01T00:00:00",
            "LastEnqueuedOffset":null,
            "RetrievalTime":"0001-01-01T00:00:00"
            }
        }''')

        return mocked_metadata

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
            'EnqueuedTimeUtc': meta.Datum(
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
