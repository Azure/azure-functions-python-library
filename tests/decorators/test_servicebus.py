#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import SERVICE_BUS_TRIGGER, \
    SERVICE_BUS
from azure.functions.decorators.core import BindingDirection, AccessRights, \
    Cardinality, DataType
from azure.functions.decorators.servicebus import ServiceBusQueueTrigger, \
    ServiceBusQueueOutput, ServiceBusTopicTrigger, \
    ServiceBusTopicOutput


class TestServiceBus(unittest.TestCase):
    def test_service_bus_queue_trigger_valid_creation(self):
        trigger = ServiceBusQueueTrigger(name="req", connection="dummy_conn",
                                         queue_name="dummy_queue",
                                         data_type=DataType.UNDEFINED,
                                         access_rights=AccessRights.MANAGE,
                                         is_sessions_enabled=True,
                                         cardinality=Cardinality.ONE,
                                         dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "serviceBusTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": SERVICE_BUS_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "connection": "dummy_conn",
            "queueName": "dummy_queue",
            "dataType": DataType.UNDEFINED,
            "accessRights": AccessRights.MANAGE,
            "isSessionsEnabled": True,
            "cardinality": Cardinality.ONE
        })

    def test_service_bus_queue_output_valid_creation(self):
        service_bus_queue_output = ServiceBusQueueOutput(
            name="res",
            connection="dummy_conn",
            queue_name="dummy_queue",
            data_type=DataType.UNDEFINED,
            access_rights=AccessRights.MANAGE,
            dummy_field="dummy")

        self.assertEqual(service_bus_queue_output.get_binding_name(),
                         "serviceBus")
        self.assertEqual(service_bus_queue_output.get_dict_repr(), {
            "type": SERVICE_BUS,
            "direction": BindingDirection.OUT,
            'dummyField': 'dummy',
            "name": "res",
            "dataType": DataType.UNDEFINED,
            "connection": "dummy_conn",
            "queueName": "dummy_queue",
            "accessRights": AccessRights.MANAGE
        })

    def test_service_bus_topic_trigger_valid_creation(self):
        trigger = ServiceBusTopicTrigger(name="req", connection="dummy_conn",
                                         topic_name="dummy_topic",
                                         subscription_name="dummy_sub",
                                         data_type=DataType.UNDEFINED,
                                         access_rights=AccessRights.MANAGE,
                                         is_sessions_enabled=True,
                                         cardinality=Cardinality.ONE,
                                         dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "serviceBusTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": SERVICE_BUS_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "connection": "dummy_conn",
            "topicName": "dummy_topic",
            "subscriptionName": "dummy_sub",
            "dataType": DataType.UNDEFINED,
            "accessRights": AccessRights.MANAGE,
            "isSessionsEnabled": True,
            "cardinality": Cardinality.ONE
        })

    def test_service_bus_topic_output_valid_creation(self):
        output = ServiceBusTopicOutput(name="res", connection="dummy_conn",
                                       topic_name="dummy_topic",
                                       subscription_name="dummy_sub",
                                       data_type=DataType.UNDEFINED,
                                       access_rights=AccessRights.MANAGE,
                                       dummy_field="dummy")

        self.assertEqual(output.get_binding_name(), "serviceBus")
        self.assertEqual(output.get_dict_repr(), {
            "type": SERVICE_BUS,
            "direction": BindingDirection.OUT,
            'dummyField': 'dummy',
            "name": "res",
            "dataType": DataType.UNDEFINED,
            "connection": "dummy_conn",
            "topicName": "dummy_topic",
            "subscriptionName": "dummy_sub",
            "accessRights": AccessRights.MANAGE
        })
