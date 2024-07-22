#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import KAFKA_TRIGGER, KAFKA
from azure.functions.decorators.core import BindingDirection, \
    DataType
from azure.functions.decorators.kafka import KafkaTrigger, KafkaOutput, \
    BrokerAuthenticationMode, BrokerProtocol


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
                               schema_registry_username="sruser",
                               schema_registry_password="srp",
                               authentication_mode=BrokerAuthenticationMode.Plain,  # noqa: E501
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "kafkaTrigger")
        self.assertEqual(trigger.get_dict_repr(),
                         {"authenticationMode": BrokerAuthenticationMode.Plain,
                          "avroSchema": "avro_schema",
                          "brokerList": "broker_list",
                          "consumerGroup": "consumer_group",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          "dummyField": "dummy",
                          "eventHubConnectionString": "ehcs",
                          "lagThreshold": 1000,
                          "name": "arg_name",
                          "password": "password",
                          "protocol": BrokerProtocol.NotSet,
                          "schemaRegistryPassword": "srp",
                          "schemaRegistryUrl": "srurl",
                          "schemaRegistryUsername": "sruser",
                          "sslCaLocation": "ssl_ca_location",
                          "sslCertificateLocation": "scl",
                          "sslKeyLocation": "ssl_key_location",
                          "sslKeyPassword": "ssl_key_password",
                          "topic": "topic",
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
                             schema_registry_username="sru",
                             schema_registry_password="srp",
                             max_retries=10,
                             data_type=DataType.UNDEFINED,
                             dummy_field="dummy")

        self.assertEqual(output.get_binding_name(), "kafka")
        self.assertEqual(output.get_dict_repr(),
                         {'authenticationMode': BrokerAuthenticationMode.NotSet,  # noqa: E501
                          'avroSchema': 'avro_schema',
                          'batchSize': 10000,
                          'brokerList': 'broker_list',
                          'dataType': DataType.UNDEFINED,
                          'direction': BindingDirection.OUT,
                          'dummyField': 'dummy',
                          'enableIdempotence': False,
                          'lingerMs': 5,
                          'maxMessageBytes': 1000000,
                          'maxRetries': 10,
                          'messageTimeoutMs': 300000,
                          'name': 'arg_name',
                          'password': 'password',
                          'protocol': BrokerProtocol.NotSet,
                          'requestTimeoutMs': 5000,
                          'schemaRegistryPassword': 'srp',
                          'schemaRegistryUrl': 'schema_registry_url',
                          'schemaRegistryUsername': 'sru',
                          'sslCaLocation': 'ssl_ca_location',
                          'sslCertificateLocation': 'scl',
                          'sslKeyLocation': 'ssl_key_location',
                          'sslKeyPassword': 'ssl_key_password',
                          'topic': 'topic',
                          'type': KAFKA,
                          'username': 'username'})
