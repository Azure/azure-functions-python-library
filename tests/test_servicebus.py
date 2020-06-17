from typing import Mapping
import json
import unittest
from datetime import datetime, timezone

import azure.functions as func
import azure.functions.servicebus as azf_sb
from azure.functions import meta


class TestServiceBus(unittest.TestCase):
    MOCKED_ENQUEUE_TIME = datetime.utcnow()

    def test_servicebus_input_type(self):
        check_input_type = (
            azf_sb.ServiceBusMessageInConverter.check_input_type_annotation
        )
        # Should accept a service bus message as trigger input type
        self.assertTrue(check_input_type(azf_sb.ServiceBusMessage))

        # Should accept a message class derived from service bus
        class ServiceBusMessageChild(azf_sb.ServiceBusMessage):
            FOO = 'BAR'

        self.assertTrue(check_input_type(ServiceBusMessageChild))

        # Should be false if a message type does not match expectation
        self.assertFalse(check_input_type(func.EventHubEvent))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(type(None)))

    def test_servicebus_output_type(self):
        check_output_type = (
            azf_sb.ServiceBusMessageOutConverter.check_output_type_annotation
        )
        # Should accept bytes and string as trigger output type
        self.assertTrue(check_output_type(bytes))
        self.assertTrue(check_output_type(str))

        # Should reject if attempt to send a service bus message out
        self.assertFalse(check_output_type(azf_sb.ServiceBusMessage))

        # Should be false if a message type does not match expectation
        self.assertFalse(check_output_type(func.EventGridEvent))
        self.assertFalse(check_output_type(type(None)))

    def test_servicebus_data(self):
        servicebus_msg = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_servicebus_data(),
            trigger_metadata=self._generate_servicebus_metadata())

        servicebus_data = servicebus_msg.get_body().decode('utf-8')
        self.assertEqual(servicebus_data, '{ "lucky_number": 23 }')

    def test_servicebus_properties(self):
        # SystemProperties in metadata should propagate to class properties
        servicebus_msg = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_servicebus_data(),
            trigger_metadata=self._generate_servicebus_metadata())

        self.assertEqual(servicebus_msg.content_type, 'application/json')
        self.assertEqual(servicebus_msg.label, 'Microsoft.Azure.ServiceBus')
        self.assertEqual(servicebus_msg.message_id,
                         '87c66eaf88e84119b66a26278a7b4149')
        self.assertEqual(servicebus_msg.enqueued_time_utc,
                         self.MOCKED_ENQUEUE_TIME)
        self.assertEqual(servicebus_msg.expires_at_utc,
                         datetime(2020, 7, 2, 5, 39, 12, 170000,
                                  tzinfo=timezone.utc))

    def test_servicebus_metadata(self):
        # Trigger metadata should contains all the essential information
        # about this service bus message
        servicebus_msg = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_servicebus_data(),
            trigger_metadata=self._generate_servicebus_metadata())

        metadata_json = servicebus_msg.metadata
        self.assertIsNotNone(metadata_json)

        # Deserialize the json back to Python dictionary
        # Datetime should be in iso8601 string instead of datetime object
        metadata_dict = json.loads(metadata_json)
        self.assertDictEqual(metadata_dict, {
            'DeliveryCount': 1,
            'LockToken': '87931fd2-39f4-415a-9fdc-adfdcbed3148',
            'ExpiresAtUtc': '2020-07-02T05:39:12.17Z',
            'EnqueuedTimeUtc': self.MOCKED_ENQUEUE_TIME.isoformat(),
            'MessageId': '87c66eaf88e84119b66a26278a7b4149',
            'ContentType': 'application/json',
            'SequenceNumber': 3,
            'Label': 'Microsoft.Azure.ServiceBus',
            'sys': {
                'MethodName': 'ServiceBusSMany',
                'UtcNow': '2020-06-18T05:39:12.2860411Z',
                'RandGuid': 'bb38deae-cc75-49f2-89f5-96ec6eb857db'
            }
        })

    def _generate_servicebus_data(self):
        return meta.Datum(value='{ "lucky_number": 23 }', type='json')

    def _generate_servicebus_metadata(self):
        mocked_metadata: Mapping[str, meta.Datum] = {}
        mocked_metadata['DeliveryCount'] = meta.Datum(1, 'int')
        mocked_metadata['LockToken'] = meta.Datum(
            '87931fd2-39f4-415a-9fdc-adfdcbed3148', 'string'
        )
        mocked_metadata['ExpiresAtUtc'] = meta.Datum(
            '2020-07-02T05:39:12.17Z', 'string'
        )
        mocked_metadata['EnqueuedTimeUtc'] = meta.Datum(
            self.MOCKED_ENQUEUE_TIME.isoformat(), 'string'
        )
        mocked_metadata['MessageId'] = meta.Datum(
            '87c66eaf88e84119b66a26278a7b4149', 'string'
        )
        mocked_metadata['ContentType'] = meta.Datum(
            'application/json', 'string'
        )
        mocked_metadata['SequenceNumber'] = meta.Datum(3, 'int')
        mocked_metadata['Label'] = meta.Datum(
            'Microsoft.Azure.ServiceBus', 'string'
        )
        mocked_metadata['sys'] = meta.Datum(type='json', value='''
            {
                "MethodName": "ServiceBusSMany",
                "UtcNow": "2020-06-18T05:39:12.2860411Z",
                "RandGuid": "bb38deae-cc75-49f2-89f5-96ec6eb857db"
            }
            ''')
        return mocked_metadata
