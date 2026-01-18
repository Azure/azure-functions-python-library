#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import KAFKA_TRIGGER, KAFKA
from azure.functions.decorators.core import BindingDirection, Cardinality, \
    DataType
from azure.functions.decorators.kafka import KafkaTrigger, KafkaOutput, \
    BrokerAuthenticationMode, BrokerProtocol, KafkaMessageKeyType


class TestKafka(unittest.TestCase):
    def test_kafka_trigger_valid_creation(self):
        trigger = KafkaTrigger(name="arg_name",
                               topic="topic",
                               broker_list="broker_list",
                               event_hub_connection_string="ehcs",
                               consumer_group="consumer_group",
                               avro_schema="avro_schema",
                               username="username",
                               password="password",
                               ssl_key_location="ssl_key_location",
                               ssl_ca_location="ssl_ca_location",
                               ssl_certificate_location="scl",
                               ssl_key_password="ssl_key_password",
                               schema_registry_url="srurl",
                               schema_registry_username="",
                               schema_registry_password="srp",
                               authentication_mode=BrokerAuthenticationMode.PLAIN,  # noqa: E501
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "kafkaTrigger")
        self.assertEqual(trigger.get_dict_repr(),
                         {"authenticationMode": BrokerAuthenticationMode.PLAIN,
                          "avroSchema": "avro_schema",
                          "brokerList": "broker_list",
                          "consumerGroup": "consumer_group",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          "dummyField": "dummy",
                          "eventHubConnectionString": "ehcs",
                          "keyDataType": KafkaMessageKeyType.STRING,
                          "lagThreshold": 1000,
                          "name": "arg_name",
                          "password": "password",
                          "protocol": BrokerProtocol.NOTSET,
                          "schemaRegistryPassword": "srp",
                          "schemaRegistryUrl": "srurl",
                          "schemaRegistryUsername": "",
                          "sslCaLocation": "ssl_ca_location",
                          "sslCertificateLocation": "scl",
                          "sslKeyLocation": "ssl_key_location",
                          "sslKeyPassword": "ssl_key_password",
                          "topic": "topic",
                          "cardinality": Cardinality.ONE,
                          "type": KAFKA_TRIGGER,
                          "username": "username"})

    def test_kafka_output_valid_creation(self):
        output = KafkaOutput(name="arg_name",
                             topic="topic",
                             broker_list="broker_list",
                             avro_schema="avro_schema",
                             username="username",
                             password="password",
                             ssl_key_location="ssl_key_location",
                             ssl_ca_location="ssl_ca_location",
                             ssl_certificate_location="scl",
                             ssl_key_password="ssl_key_password",
                             schema_registry_url="schema_registry_url",
                             schema_registry_username="",
                             schema_registry_password="srp",
                             max_retries=10,
                             data_type=DataType.UNDEFINED,
                             dummy_field="dummy")

        self.assertEqual(output.get_binding_name(), "kafka")
        self.assertEqual(output.get_dict_repr(),
                         {'authenticationMode': BrokerAuthenticationMode.NOTSET,
                          'avroSchema': 'avro_schema',
                          'batchSize': 10000,
                          'brokerList': 'broker_list',
                          'dataType': DataType.UNDEFINED,
                          'direction': BindingDirection.OUT,
                          'dummyField': 'dummy',
                          'enableIdempotence': False,
                          'keyDataType': KafkaMessageKeyType.STRING,
                          'lingerMs': 5,
                          'maxMessageBytes': 1000000,
                          'maxRetries': 10,
                          'messageTimeoutMs': 300000,
                          'name': 'arg_name',
                          'password': 'password',
                          'protocol': BrokerProtocol.NOTSET,
                          'requestTimeoutMs': 5000,
                          'schemaRegistryPassword': 'srp',
                          'schemaRegistryUrl': 'schema_registry_url',
                          'schemaRegistryUsername': '',
                          'sslCaLocation': 'ssl_ca_location',
                          'sslCertificateLocation': 'scl',
                          'sslKeyLocation': 'ssl_key_location',
                          'sslKeyPassword': 'ssl_key_password',
                          'topic': 'topic',
                          'type': KAFKA,
                          'username': 'username'})

    def test_kafka_trigger_with_key_data_type_and_pem(self):
        trigger = KafkaTrigger(name="arg_name",
                               topic="topic",
                               broker_list="broker_list",
                               key_avro_schema="key_avro_schema",
                               key_data_type=KafkaMessageKeyType.LONG,
                               ssl_certificate_pem="cert_pem",
                               ssl_key_pem="key_pem",
                               ssl_ca_pem="ca_pem",
                               ssl_certificate_and_key_pem="cert_and_key_pem",
                               data_type=DataType.UNDEFINED)

        self.assertEqual(trigger.get_binding_name(), "kafkaTrigger")
        dict_repr = trigger.get_dict_repr()
        self.assertEqual(dict_repr["keyAvroSchema"], "key_avro_schema")
        self.assertEqual(dict_repr["keyDataType"], KafkaMessageKeyType.LONG)
        self.assertEqual(dict_repr["sslCertificatePem"], "cert_pem")
        self.assertEqual(dict_repr["sslKeyPem"], "key_pem")
        self.assertEqual(dict_repr["sslCaPem"], "ca_pem")
        self.assertEqual(dict_repr["sslCertificateAndKeyPem"], "cert_and_key_pem")

    def test_kafka_output_with_key_data_type_and_pem(self):
        output = KafkaOutput(name="arg_name",
                             topic="topic",
                             broker_list="broker_list",
                             avro_schema="avro_schema",
                             key_avro_schema="key_avro_schema",
                             key_data_type=KafkaMessageKeyType.BINARY,
                             ssl_certificate_pem="cert_pem",
                             ssl_key_pem="key_pem",
                             ssl_ca_pem="ca_pem",
                             ssl_certificate_and_key_pem="cert_and_key_pem",
                             data_type=DataType.UNDEFINED)

        self.assertEqual(output.get_binding_name(), "kafka")
        dict_repr = output.get_dict_repr()
        self.assertEqual(dict_repr["keyAvroSchema"], "key_avro_schema")
        self.assertEqual(dict_repr["keyDataType"], KafkaMessageKeyType.BINARY)
        self.assertEqual(dict_repr["sslCertificatePem"], "cert_pem")
        self.assertEqual(dict_repr["sslKeyPem"], "key_pem")
        self.assertEqual(dict_repr["sslCaPem"], "ca_pem")
        self.assertEqual(dict_repr["sslCertificateAndKeyPem"], "cert_and_key_pem")

    def test_kafka_message_key_type_enum(self):
        """Test that KafkaMessageKeyType enum has the correct values"""
        self.assertEqual(KafkaMessageKeyType.INT.value, 0)
        self.assertEqual(KafkaMessageKeyType.LONG.value, 1)
        self.assertEqual(KafkaMessageKeyType.STRING.value, 2)
        self.assertEqual(KafkaMessageKeyType.BINARY.value, 3)

    def test_kafka_trigger_key_data_type_default(self):
        """Test that key_data_type defaults to STRING"""
        trigger = KafkaTrigger(name="arg_name",
                               topic="topic",
                               broker_list="broker_list")

        dict_repr = trigger.get_dict_repr()
        self.assertEqual(dict_repr["keyDataType"], KafkaMessageKeyType.STRING)

    def test_kafka_output_key_data_type_default(self):
        """Test that key_data_type defaults to STRING"""
        output = KafkaOutput(name="arg_name",
                             topic="topic",
                             broker_list="broker_list",
                             avro_schema="schema")

        dict_repr = output.get_dict_repr()
        self.assertEqual(dict_repr["keyDataType"], KafkaMessageKeyType.STRING)
