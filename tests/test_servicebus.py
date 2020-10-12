# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Dict, List
import json
import unittest
from datetime import datetime, timedelta

import azure.functions as func
import azure.functions.servicebus as azf_sb
from azure.functions import meta

from .testutils import CollectionBytes, CollectionString, CollectionSint64


class TestServiceBus(unittest.TestCase):
    MOCKED_CONTENT_TYPE = 'application/json'
    MOCKED_CORROLATION_ID = '87c66eaf88e84119b66a26278a7b4149'
    MOCKED_DEADLETTER_SOURCE = 'mocked_dead_letter_source'
    MOCKED_DELIVERY_COUNT = 571
    MOCKED_ENQUEUED_SEQUENCE_NUMBER = 4132
    MOCKED_ENQUEUED_SEQUENCE_NUMBER_A = 11111
    MOCKED_ENQUEUED_SEQUENCE_NUMBER_B = 22222
    MOCKED_ENQUEUED_SEQUENCE_NUMBER_C = 33333
    MOCKED_ENQUEUE_TIME_UTC = datetime.utcnow()
    MOCKED_EXPIRY_AT_UTC = datetime.utcnow()
    MOCKED_LABEL = 'mocked_label'
    MOCKED_LOCKED_UNTIL_UTC = datetime.utcnow()
    MOCKED_LOCK_TOKEN = '87931fd2-39f4-415a-9fdc-adfdcbed3148'
    MOCKED_MESSAGE_ID = 'abcee18397398d93891830a0aac89eed'
    MOCKED_PARTITION_KEY = 'mocked_partition_key'
    MOCKED_REPLY_TO = 'mocked_reply_to'
    MOCKED_REPLY_TO_SESSION_ID = 'mocked_reply_to_session_id'
    MOCKED_SCHEDULED_ENQUEUE_TIME_UTC = datetime.utcnow()
    MOCKED_SEQUENCE_NUMBER = 38291
    MOCKED_SESSION_ID = 'mocked_session_id'
    MOCKED_TIME_TO_LIVE = '11:22:33'
    MOCKED_TIME_TO_LIVE_TIMEDELTA = timedelta(hours=11, minutes=22, seconds=33)
    MOCKED_TO = 'mocked_to'
    MOCKED_VIA_PARTITION_KEY = 'mocked_via_partition_key'

    MOCKED_AZURE_PARTNER_ID = '6ceef68b-0794-45dd-bb2e-630748515552'

    def test_servicebus_input_type(self):
        check_input_type = (
            azf_sb.ServiceBusMessageInConverter.check_input_type_annotation
        )
        # Should accept a single service bus message as trigger input type
        self.assertTrue(check_input_type(func.ServiceBusMessage))

        # Should accept a multiple service bus message as trigger input type
        self.assertTrue(check_input_type(List[func.ServiceBusMessage]))

        # Should accept a message class derived from service bus
        class ServiceBusMessageChild(func.ServiceBusMessage):
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
        self.assertFalse(check_output_type(func.ServiceBusMessage))

        # Should be false if a message type does not match expectation
        self.assertFalse(check_output_type(func.EventGridEvent))
        self.assertFalse(check_output_type(type(None)))

    def test_servicebus_data(self):
        servicebus_msg = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_single_servicebus_data(),
            trigger_metadata=self._generate_single_trigger_metadata())

        servicebus_data = servicebus_msg.get_body().decode('utf-8')
        self.assertEqual(servicebus_data, json.dumps({"lucky_number": 23}))

    def test_servicebus_properties(self):
        # SystemProperties in metadata should propagate to class properties
        msg = azf_sb.ServiceBusMessageInConverter.decode(
            data=meta.Datum(b'body_bytes', 'bytes'),
            trigger_metadata=self._generate_single_trigger_metadata())

        self.assertEqual(msg.get_body(), b'body_bytes')

        # Test individual ServiceBus properties respectively
        self.assertEqual(msg.content_type,
                         self.MOCKED_CONTENT_TYPE)
        self.assertEqual(msg.correlation_id,
                         self.MOCKED_CORROLATION_ID)
        self.assertEqual(msg.dead_letter_source,
                         self.MOCKED_DEADLETTER_SOURCE)
        self.assertEqual(msg.enqueued_sequence_number,
                         self.MOCKED_ENQUEUED_SEQUENCE_NUMBER)
        self.assertEqual(msg.enqueued_time_utc,
                         self.MOCKED_ENQUEUE_TIME_UTC)
        self.assertEqual(msg.expires_at_utc,
                         self.MOCKED_EXPIRY_AT_UTC)
        self.assertEqual(msg.expiration_time,
                         self.MOCKED_EXPIRY_AT_UTC)
        self.assertEqual(msg.label,
                         self.MOCKED_LABEL)
        self.assertEqual(msg.locked_until_utc,
                         self.MOCKED_LOCKED_UNTIL_UTC)
        self.assertEqual(msg.message_id,
                         self.MOCKED_MESSAGE_ID)
        self.assertEqual(msg.partition_key,
                         self.MOCKED_PARTITION_KEY)
        self.assertEqual(msg.reply_to,
                         self.MOCKED_REPLY_TO)
        self.assertEqual(msg.reply_to_session_id,
                         self.MOCKED_REPLY_TO_SESSION_ID)
        self.assertEqual(msg.scheduled_enqueue_time,
                         self.MOCKED_SCHEDULED_ENQUEUE_TIME_UTC)
        self.assertEqual(msg.scheduled_enqueue_time_utc,
                         self.MOCKED_SCHEDULED_ENQUEUE_TIME_UTC)
        self.assertEqual(msg.session_id,
                         self.MOCKED_SESSION_ID)
        self.assertEqual(msg.time_to_live,
                         self.MOCKED_TIME_TO_LIVE_TIMEDELTA)
        self.assertEqual(msg.to,
                         self.MOCKED_TO)
        self.assertDictEqual(msg.user_properties, {
            '$AzureWebJobsParentId': self.MOCKED_AZURE_PARTNER_ID,
            'x-opt-enqueue-sequence-number': 0
        })

    def test_servicebus_metadata(self):
        # Trigger metadata should contains all the essential information
        # about this service bus message
        servicebus_msg = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_single_servicebus_data(),
            trigger_metadata=self._generate_single_trigger_metadata())

        # Datetime should be in iso8601 string instead of datetime object
        metadata_dict = servicebus_msg.metadata
        self.assertGreaterEqual(metadata_dict.items(), {
            'DeliveryCount': self.MOCKED_DELIVERY_COUNT,
            'LockToken': self.MOCKED_LOCK_TOKEN,
            'ExpiresAtUtc': self.MOCKED_EXPIRY_AT_UTC.isoformat(),
            'EnqueuedTimeUtc': self.MOCKED_ENQUEUE_TIME_UTC.isoformat(),
            'MessageId': self.MOCKED_MESSAGE_ID,
            'ContentType': self.MOCKED_CONTENT_TYPE,
            'SequenceNumber': self.MOCKED_SEQUENCE_NUMBER,
            'Label': self.MOCKED_LABEL,
            'sys': {
                'MethodName': 'ServiceBusSMany',
                'UtcNow': '2020-06-18T05:39:12.2860411Z',
                'RandGuid': 'bb38deae-cc75-49f2-89f5-96ec6eb857db'
            }
        }.items())

    def test_servicebus_should_not_override_metadata(self):
        # SystemProperties in metadata should propagate to class properties
        servicebus_msg = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_single_servicebus_data(),
            trigger_metadata=self._generate_single_trigger_metadata())

        # The content_type trigger field should be set
        self.assertEqual(servicebus_msg.content_type, 'application/json')

        # The metadata field should also be set
        self.assertEqual(servicebus_msg.metadata['ContentType'],
                         'application/json')

        # Now we change the metadata field
        # The trigger property should still remain the same
        servicebus_msg.metadata['ContentType'] = 'text/plain'
        self.assertEqual(servicebus_msg.content_type, 'application/json')

    def test_multiple_servicebus_trigger(self):
        # When cardinality is turned on to 'many', metadata should contain
        # information for all messages
        servicebus_msgs = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_multiple_service_bus_data(),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )

        # The decoding result should contain a list of message
        self.assertEqual(len(servicebus_msgs), 3)

    def test_multiple_servicebus_trigger_properties(self):
        # When cardinality is turned on to 'many', metadata should contain
        # information for all messages
        servicebus_msgs = azf_sb.ServiceBusMessageInConverter.decode(
            data=self._generate_multiple_service_bus_data(),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )

        expceted_bodies: List[str] = [
            json.dumps({"lucky_number": 23}),
            json.dumps({"lucky_number": 34}),
            json.dumps({"lucky_number": 45}),
        ]

        expected_enqueued_sequence_number: List[int] = [
            self.MOCKED_ENQUEUED_SEQUENCE_NUMBER_A,
            self.MOCKED_ENQUEUED_SEQUENCE_NUMBER_B,
            self.MOCKED_ENQUEUED_SEQUENCE_NUMBER_C
        ]

        for i in range(len(servicebus_msgs)):
            msg = servicebus_msgs[i]
            body_data = msg.get_body().decode('utf-8')
            self.assertEqual(body_data, expceted_bodies[i])

            self.assertEqual(msg.content_type,
                             self.MOCKED_CONTENT_TYPE)
            self.assertEqual(msg.correlation_id,
                             self.MOCKED_CORROLATION_ID)
            self.assertEqual(msg.dead_letter_source,
                             self.MOCKED_DEADLETTER_SOURCE)
            self.assertEqual(msg.enqueued_sequence_number,
                             expected_enqueued_sequence_number[i])
            self.assertEqual(msg.enqueued_time_utc,
                             self.MOCKED_ENQUEUE_TIME_UTC)
            self.assertEqual(msg.expires_at_utc,
                             self.MOCKED_EXPIRY_AT_UTC)
            self.assertEqual(msg.expiration_time,
                             self.MOCKED_EXPIRY_AT_UTC)
            self.assertEqual(msg.label,
                             self.MOCKED_LABEL)
            self.assertEqual(msg.locked_until_utc,
                             self.MOCKED_LOCKED_UNTIL_UTC)
            self.assertEqual(msg.message_id,
                             self.MOCKED_MESSAGE_ID)
            self.assertEqual(msg.partition_key,
                             self.MOCKED_PARTITION_KEY)
            self.assertEqual(msg.reply_to,
                             self.MOCKED_REPLY_TO)
            self.assertEqual(msg.reply_to_session_id,
                             self.MOCKED_REPLY_TO_SESSION_ID)
            self.assertEqual(msg.scheduled_enqueue_time,
                             self.MOCKED_SCHEDULED_ENQUEUE_TIME_UTC)
            self.assertEqual(msg.scheduled_enqueue_time_utc,
                             self.MOCKED_SCHEDULED_ENQUEUE_TIME_UTC)
            self.assertEqual(msg.session_id,
                             self.MOCKED_SESSION_ID)
            self.assertEqual(msg.time_to_live,
                             self.MOCKED_TIME_TO_LIVE_TIMEDELTA)
            self.assertEqual(msg.to,
                             self.MOCKED_TO)
            self.assertDictEqual(msg.user_properties, {
                '$AzureWebJobsParentId': self.MOCKED_AZURE_PARTNER_ID,
                'x-opt-enqueue-sequence-number': 0
            })

    def _generate_single_servicebus_data(self) -> meta.Datum:
        return meta.Datum(value=json.dumps({
            'lucky_number': 23
        }), type='json')

    def _generate_multiple_service_bus_data(self) -> meta.Datum:
        return meta.Datum(value=json.dumps([
            {'lucky_number': 23},
            {'lucky_number': 34},
            {'lucky_number': 45}
        ]), type='json')

    def _generate_single_trigger_metadata(self) -> Dict[str, meta.Datum]:
        """Generate a single ServiceBus message following
        https://docs.microsoft.com/en-us/azure/service-bus-messaging/
        service-bus-messages-payloads
        """

        mocked_metadata: Dict[str, meta.Datum] = {
            'ContentType': meta.Datum(
                self.MOCKED_CONTENT_TYPE, 'string'
            ),
            'CorrelationId': meta.Datum(
                self.MOCKED_CORROLATION_ID, 'string'
            ),
            'DeadLetterSource': meta.Datum(
                self.MOCKED_DEADLETTER_SOURCE, 'string'
            ),
            'DeliveryCount': meta.Datum(
                self.MOCKED_DELIVERY_COUNT, 'int'
            ),
            'EnqueuedSequenceNumber': meta.Datum(
                self.MOCKED_ENQUEUED_SEQUENCE_NUMBER, 'int'
            ),
            'EnqueuedTimeUtc': meta.Datum(
                self.MOCKED_ENQUEUE_TIME_UTC.isoformat(), 'string'
            ),
            'ExpiresAtUtc': meta.Datum(
                self.MOCKED_EXPIRY_AT_UTC.isoformat(), 'string'
            ),
            # 'ForcePersistence' not exposed yet, requires gRPC boolean passing
            'Label': meta.Datum(
                self.MOCKED_LABEL, 'string'
            ),
            'LockedUntilUtc': meta.Datum(
                self.MOCKED_LOCKED_UNTIL_UTC.isoformat(), 'string'
            ),
            'LockToken': meta.Datum(
                self.MOCKED_LOCK_TOKEN, 'string'
            ),
            'MessageId': meta.Datum(
                self.MOCKED_MESSAGE_ID, 'string'
            ),
            'PartitionKey': meta.Datum(
                self.MOCKED_PARTITION_KEY, 'string'
            ),
            'ReplyTo': meta.Datum(
                self.MOCKED_REPLY_TO, 'string'
            ),
            'ReplyToSessionId': meta.Datum(
                self.MOCKED_REPLY_TO_SESSION_ID, 'string'
            ),
            'ScheduledEnqueueTimeUtc': meta.Datum(
                self.MOCKED_SCHEDULED_ENQUEUE_TIME_UTC.isoformat(), 'string'
            ),
            'SequenceNumber': meta.Datum(
                self.MOCKED_SEQUENCE_NUMBER, 'int'
            ),
            'SessionId': meta.Datum(
                self.MOCKED_SESSION_ID, 'string'
            ),
            'TimeToLive': meta.Datum(
                self.MOCKED_TIME_TO_LIVE, 'string'
            ),
            'To': meta.Datum(
                self.MOCKED_TO, 'string'
            ),
            'ViaPartitionKey': meta.Datum(
                self.MOCKED_VIA_PARTITION_KEY, 'string'
            )
        }
        mocked_metadata['MessageReceiver'] = meta.Datum(type='json', value='''
        {
            "RegisteredPlugins": [],
            "ReceiveMode": 0,
            "PrefetchCount": 0,
            "LastPeekedSequenceNumber": 0,
            "Path": "testqueue",
            "OperationTimeout": "00:01:00",
            "ServiceBusConnection": {
                "Endpoint": "sb://python-worker-36-sbns.servicebus.win.net",
                "OperationTimeout": "00:01:00",
                "RetryPolicy": {
                    "MinimalBackoff": "00:00:00",
                    "MaximumBackoff": "00:00:30",
                    "DeltaBackoff": "00:00:03",
                    "MaxRetryCount": 5,
                    "IsServerBusy": false,
                    "ServerBusyExceptionMessage": null
                },
                "TransportType": 0,
                "TokenProvider": {}
            },
            "IsClosedOrClosing": false,
            "ClientId": "MessageReceiver1testqueue",
            "RetryPolicy": {
                "MinimalBackoff": "00:00:00",
                "MaximumBackoff": "00:00:30",
                "DeltaBackoff": "00:00:03",
                "MaxRetryCount": 5,
                "IsServerBusy": false,
                "ServerBusyExceptionMessage": null
            }
        }''')
        mocked_metadata['UserProperties'] = meta.Datum(type='json', value='''
        {
            "$AzureWebJobsParentId": "6ceef68b-0794-45dd-bb2e-630748515552",
            "x-opt-enqueue-sequence-number": 0
        }''')
        mocked_metadata['sys'] = meta.Datum(type='json', value='''
        {
            "MethodName": "ServiceBusSMany",
            "UtcNow": "2020-06-18T05:39:12.2860411Z",
            "RandGuid": "bb38deae-cc75-49f2-89f5-96ec6eb857db"
        }
        ''')
        return mocked_metadata

    def _generate_multiple_trigger_metadata(self) -> Dict[str, meta.Datum]:
        """Generate a metadatum containing 3 service bus messages which can be
        distingushed by enqueued_sequence_number
        """
        sb_a = self._generate_single_trigger_metadata()
        sb_b = self._generate_single_trigger_metadata()
        sb_c = self._generate_single_trigger_metadata()

        sb_a['EnqueuedSequenceNumber'] = meta.Datum(
            value=self.MOCKED_ENQUEUED_SEQUENCE_NUMBER_A,
            type='int'
        )
        sb_b['EnqueuedSequenceNumber'] = meta.Datum(
            value=self.MOCKED_ENQUEUED_SEQUENCE_NUMBER_B,
            type='int'
        )
        sb_b['EnqueuedSequenceNumber'] = meta.Datum(
            value=self.MOCKED_ENQUEUED_SEQUENCE_NUMBER_C,
            type='int'
        )

        combine_from = lambda key, et: self._zip(key, et, sb_a, sb_b, sb_c)

        mocked_metadata = {
            'ContentTypeArray': combine_from(
                'ContentType', 'collection_string'
            ),
            'CorrelationIdArray': combine_from(
                'CorrelationId', 'collection_string'
            ),
            'DeadLetterSourceArray': combine_from(
                'DeadLetterSource', 'collection_string'
            ),
            'EnqueuedSequenceNumberArray': combine_from(
                'EnqueuedSequenceNumber', 'collection_sint64'
            ),
            'EnqueuedTimeUtcArray': combine_from(
                'EnqueuedTimeUtc', 'json'
            ),
            'ExpiresAtUtcArray': combine_from(
                'ExpiresAtUtc', 'json'
            ),
            'LabelArray': combine_from(
                'Label', 'collection_string'
            ),
            'LockTokenArray': combine_from(
                'LockToken', 'collection_string'
            ),
            'MessageIdArray': combine_from(
                'MessageId', 'collection_string'
            ),
            'ReplyToArray': combine_from(
                'ReplyTo', 'collection_string'
            ),
            'SequenceNumberArray': combine_from(
                'SequenceNumber', 'collection_sint64'
            ),
            'ToArray': combine_from(
                'To', 'collection_string'
            ),
            'UserPropertiesArray': combine_from(
                'UserProperties', 'json'
            )
        }

        return mocked_metadata

    def _zip(self, key: str, expected_type: str,
             *args: List[Dict[str, meta.Datum]]) -> meta.Datum:
        """Combining multiple metadata into one:
        string -> collection_string
        bytes -> collection_bytes
        int -> collection_sint64
        sint64 -> collection_sint64
        json -> json (with array in it)
        """
        convertible = {
            'collection_string': CollectionString,
            'collection_bytes': CollectionBytes,
            'collection_sint64': CollectionSint64
        }

        datum_type = args[0][key].type
        if expected_type in convertible.keys():
            return meta.Datum(
                value=convertible[expected_type]([d[key].value for d in args]),
                type=expected_type
            )
        elif expected_type == 'json':
            if datum_type == 'json':
                value = json.dumps([json.loads(d[key].value) for d in args])
            else:
                value = json.dumps([d[key].value for d in args])
            return meta.Datum(
                value=value,
                type='json'
            )
        else:
            raise NotImplementedError(f'Unknown convertion {key}: '
                                      f'{datum_type} -> {expected_type}')
