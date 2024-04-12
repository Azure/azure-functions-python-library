# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List
import unittest
import json

from unittest.mock import patch
import azure.functions as func
import azure.functions.kafka as azf_ka
import azure.functions.meta as meta

from tests.utils.testutils import (CollectionBytes, CollectionString,
                                   CollectionSint64)


class Kafka(unittest.TestCase):
    SINGLE_KAFKA_DATAUM = '{"Offset":1,"Partition":0,"Topic":"users",'\
        '"Timestamp":"2020-06-20T04:43:28.998Z","Value":"hello", ' \
                          '"Headers":[{"Key":"test","Value":"1"}]}'
    SINGLE_KAFKA_TIMESTAMP = "2020-06-20T04:43:28.998Z"
    MULTIPLE_KAFKA_TIMESTAMP_0 = "2020-06-20T05:06:25.139Z"
    MULTIPLE_KAFKA_TIMESTAMP_1 = "2020-06-20T05:06:25.945Z"
    MULTIPLE_KAFKA_DATA_0 = '{"Offset":62,"Partition":1,"Topic":"message",'\
        '"Timestamp":"2020-06-20T05:06:25.139Z","Value":"a", ' \
                            '"Headers":[{"Key":"test","Value":"1"}], ' \
                            '"Key" : "1"}'
    MULTIPLE_KAFKA_DATA_1 = '{"Offset":63,"Partition":1,"Topic":"message",'\
        '"Timestamp":"2020-06-20T05:06:25.945Z","Value":"a", ' \
                            '"Headers":[{"Key":"test2","Value":"2"}], ' \
                            '"Key": "2"}'

    def test_kafka_input_type(self):
        check_input_type = (
            azf_ka.KafkaConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(func.KafkaEvent))
        self.assertTrue(check_input_type(List[func.KafkaEvent]))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))
        self.assertFalse(check_input_type(List[str]))

    def test_kafka_output_type(self):
        check_output_type = (
            azf_ka.KafkaTriggerConverter.check_output_type_annotation
        )
        self.assertTrue(check_output_type(bytes))
        self.assertTrue(check_output_type(str))
        self.assertTrue(check_output_type(List[str]))
        self.assertFalse(check_output_type(func.KafkaEvent))
        self.assertFalse(check_output_type(List[bytes]))
        self.assertFalse(check_output_type(List[func.KafkaEvent]))

    @patch('azure.functions.kafka.KafkaTriggerConverter'
           '.decode_single_event')
    @patch('azure.functions.kafka.KafkaTriggerConverter'
           '.decode_multiple_events')
    def test_kafka_decode_single_event(self, dme_mock, dse_mock):
        azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_single_kafka_datum(),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        dse_mock.assert_called_once()
        dme_mock.assert_not_called()

    @patch('azure.functions.kafka.KafkaTriggerConverter'
           '.decode_single_event')
    @patch('azure.functions.kafka.KafkaTriggerConverter'
           '.decode_multiple_events')
    def test_kafka_decode_multiple_events(self, dse_mock, dme_mock):
        azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_multiple_kafka_data(),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        dse_mock.assert_not_called()
        dme_mock.assert_called_once()

    def test_kafka_trigger_single_event_json(self):
        result = azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_single_kafka_datum('json'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        # Result body always has the datatype of bytes
        self.assertEqual(
            result.get_body().decode('utf-8'), self.SINGLE_KAFKA_DATAUM
        )
        self.assertEqual(result.timestamp, self.SINGLE_KAFKA_TIMESTAMP)

    def test_kafka_trigger_single_event_bytes(self):
        result = azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_single_kafka_datum('bytes'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        self.assertEqual(
            result.get_body().decode('utf-8'), self.SINGLE_KAFKA_DATAUM
        )
        self.assertEqual(result.timestamp, self.SINGLE_KAFKA_TIMESTAMP)

    def test_kafka_trigger_single_event_string(self):
        result = azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_single_kafka_datum('string'),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )
        self.assertEqual(
            result.get_body().decode('utf-8'), self.SINGLE_KAFKA_DATAUM
        )
        self.assertEqual(result.timestamp, self.SINGLE_KAFKA_TIMESTAMP)

    def test_kafka_trigger_multiple_events_collection_string(self):
        result = azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_multiple_kafka_data('collection_string'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0].timestamp,
            self.MULTIPLE_KAFKA_TIMESTAMP_0)
        self.assertEqual(
            json.loads(result[0].get_body().decode('utf-8')),
            json.loads(self.MULTIPLE_KAFKA_DATA_0)
        )

        self.assertEqual(
            result[1].timestamp,
            self.MULTIPLE_KAFKA_TIMESTAMP_1)
        self.assertEqual(
            json.loads(result[1].get_body().decode('utf-8')),
            json.loads(self.MULTIPLE_KAFKA_DATA_1)
        )

    def test_kafka_trigger_multiple_events_collection_bytes(self):
        result = azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_multiple_kafka_data('collection_bytes'),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0].timestamp,
            self.MULTIPLE_KAFKA_TIMESTAMP_0)
        self.assertEqual(
            json.loads(result[0].get_body().decode('utf-8')),
            json.loads(self.MULTIPLE_KAFKA_DATA_0)
        )

        self.assertEqual(
            result[1].timestamp,
            self.MULTIPLE_KAFKA_TIMESTAMP_1)
        self.assertEqual(
            json.loads(result[1].get_body().decode('utf-8')),
            json.loads(self.MULTIPLE_KAFKA_DATA_1)
        )

    def test_single_kafka_trigger_metadata_field(self):
        result = azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_single_kafka_datum(),
            trigger_metadata=self._generate_single_trigger_metadatum()
        )

        # Timestamp
        self.assertEqual(result.timestamp, self.SINGLE_KAFKA_TIMESTAMP)
        # Offset should be 1
        self.assertEqual(result.offset, 1)
        # Topic
        self.assertEqual(result.topic, "users")
        # Partition
        self.assertEqual(result.partition, 0)
        # Value
        self.assertEqual(
            json.loads(result.get_body().decode('utf-8'))['Value'], "hello")
        # Metadata
        metadata_dict = result.metadata
        sys = metadata_dict['sys']
        sys_dict = json.loads(sys)
        self.assertEqual(sys_dict['MethodName'], 'KafkaTrigger')

    def test_multiple_kafka_triggers_metadata_field(self):
        result = azf_ka.KafkaTriggerConverter.decode(
            data=self._generate_multiple_kafka_data("collection_string"),
            trigger_metadata=self._generate_multiple_trigger_metadata()
        )

        self.assertEqual(result[0].offset, 62)
        self.assertEqual(result[1].offset, 63)

        self.assertEqual(result[0].partition, 1)
        self.assertEqual(result[1].partition, 2)

        self.assertEqual(
            result[0].timestamp,
            "2020-06-20T05:06:25.139Z")
        self.assertEqual(
            result[1].timestamp,
            "2020-06-20T05:06:25.945Z")
        metadata_dict = result[0].metadata
        sys = metadata_dict['sys']
        sys_dict = json.loads(sys)
        self.assertEqual(sys_dict['MethodName'], 'KafkaTriggerMany')

    def test_kafka_convert_single_event_str(self):
        datum = meta.Datum("dummy_body", "string")
        result = azf_ka.KafkaConverter.decode(
            data=datum, trigger_metadata=None)

        self.assertEqual(result.get_body(), b"dummy_body")

    def test_kafka_convert_single_event_bytes(self):
        datum = meta.Datum(b"dummy_body", "bytes")
        result = azf_ka.KafkaConverter.decode(
            data=datum, trigger_metadata=None)

        self.assertEqual(result.get_body(), b"dummy_body")

    def test_kafka_convert_multiple_event_collection_string(self):
        datum = meta.Datum(CollectionString(["dummy_body1", "dummy_body2"]),
                           "collection_string")
        result = azf_ka.KafkaConverter.decode(
            data=datum, trigger_metadata=None)

        self.assertEqual([result[0].get_body(), result[1].get_body()],
                         [b"dummy_body1", b"dummy_body2"])

    def test_kafka_convert_multiple_event_collection_bytes(self):
        datum = meta.Datum(CollectionBytes([b"dummy_body1", b"dummy_body2"]),
                           "collection_bytes")
        result = azf_ka.KafkaConverter.decode(
            data=datum, trigger_metadata=None)

        self.assertEqual([result[0].get_body(), result[1].get_body()],
                         [b"dummy_body1", b"dummy_body2"])

    def _generate_single_kafka_datum(self, datum_type='string'):
        datum = self.SINGLE_KAFKA_DATAUM
        if datum_type == 'bytes':
            datum = datum.encode('utf-8')
        return meta.Datum(datum, datum_type)

    def _generate_multiple_kafka_data(self, data_type='json'):
        data = '[{"Offset":62,"Partition":1,"Topic":"message",'\
               '"Timestamp":"2020-06-20T05:06:25.139Z","Value":"a",' \
               ' "Headers":[{"Key":"test","Value":"1"}], "Key": "1"},'\
               ' {"Offset":63,"Partition":1,"Topic":"message",'\
               '"Timestamp":"2020-06-20T05:06:25.945Z","Value":"a", ' \
               '"Headers":[{"Key":"test2","Value":"2"}], "Key": "2"}]'
        if data_type == 'collection_bytes':
            data = list(
                map(lambda x: json.dumps(x).encode('utf-8'),
                    json.loads(data))
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
            'Offset': meta.Datum(
                '1', 'string'
            ),
            'Partition': meta.Datum(
                '0', 'string'
            ),
            'Timestamp': meta.Datum(
                self.SINGLE_KAFKA_TIMESTAMP, 'string'
            ),
            'Topic': meta.Datum(
                'users', 'string'
            ),
            'Value': meta.Datum(
                'hello', 'string'
            ),
            'sys': meta.Datum(
                '{"MethodName":"KafkaTrigger",'
                '"UtcNow":"2020-06-20T04:43:30.6756278Z",'
                '"RandGuid":"b0870c0c-2b7a-40dc-b4be-45224c91a49c"}',
                'json'
            )  # __len__: 6
        }

    def _generate_multiple_trigger_metadata(self):
        key_array = ["1", "2"]
        partition_array = [1, 2]
        timestamp_array = ["2020-06-20T05:06:25.139Z",
                           "2020-06-20T05:06:25.945Z"]

        return {
            'KeyArray': meta.Datum(
                json.dumps(key_array), 'json'
            ),
            'OffsetArray': meta.Datum(
                CollectionSint64([62, 63]), 'collection_sint64'
            ),
            'PartitionArray': meta.Datum(
                json.dumps(partition_array), 'json'
            ),
            'TimestampArray': meta.Datum(
                json.dumps(timestamp_array), 'json'
            ),
            'TopicArray': meta.Datum(
                CollectionString(['message', 'message']), "collection_string"
            ),
            'HeadersArray': meta.Datum(
                json.dumps([['{"Key":"test","Value":"1"}'],
                            ['{"Key":"test2","Value":"2"}']]), 'json'
            ),
            'sys': meta.Datum(
                '{"MethodName":"KafkaTriggerMany",'
                '"UtcNow":"2020-06-20T05:06:26.5550868Z",'
                '"RandGuid":"57d5eeb7-c86c-4924-a14a-160092154093"}',
                'json'
            )
        }
