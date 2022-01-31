#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions import DataType
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.servicebus import ServiceBusQueueTrigger, \
    ServiceBusQueueOutput, ServiceBusTopicTrigger, \
    ServiceBusTopicOutput
from azure.functions.decorators import Cardinality, AccessRights


class TestServiceBus(unittest.TestCase):
    def test_service_bus_queue_trigger_valid_creation(self):
        trigger = ServiceBusQueueTrigger(name="req", connection="dummy_conn",
                                         queue_name="dummy_queue",
                                         data_type=DataType.UNDEFINED,
                                         access_rights=AccessRights.MANAGE,
                                         is_sessions_enabled=True,
                                         cardinality=Cardinality.ONE)

        self.assertEqual(trigger.get_binding_name(), "serviceBusTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "serviceBusTrigger",
            "direction": str(BindingDirection.IN),
            "name": "req",
            "connection": "dummy_conn",
            "queueName": "dummy_queue",
            "dataType": str(DataType.UNDEFINED),
            "accessRights": str(AccessRights.MANAGE.value),
            "isSessionsEnabled": True,
            "cardinality": str(Cardinality.ONE.value)
        })

    def test_service_bus_queue_output_valid_creation(self):
        service_bus_queue_output = ServiceBusQueueOutput(
            name="res",
            connection="dummy_conn",
            queue_name="dummy_queue",
            data_type=DataType.UNDEFINED,
            access_rights=AccessRights.MANAGE)

        self.assertEqual(service_bus_queue_output.get_binding_name(),
                         "serviceBus")
        self.assertEqual(service_bus_queue_output.get_dict_repr(), {
            "type": "serviceBus",
            "direction": str(BindingDirection.OUT),
            "name": "res",
            "dataType": str(DataType.UNDEFINED),
            "connection": "dummy_conn",
            "queueName": "dummy_queue",
            "accessRights": str(AccessRights.MANAGE.value)
        })

    def test_service_bus_topic_trigger_valid_creation(self):
        trigger = ServiceBusTopicTrigger(name="req", connection="dummy_conn",
                                         topic_name="dummy_topic",
                                         subscription_name="dummy_sub",
                                         data_type=DataType.UNDEFINED,
                                         access_rights=AccessRights.MANAGE,
                                         is_sessions_enabled=True,
                                         cardinality=Cardinality.ONE)

        self.assertEqual(trigger.get_binding_name(), "serviceBusTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "serviceBusTrigger",
            "direction": str(BindingDirection.IN),
            "name": "req",
            "connection": "dummy_conn",
            "topicName": "dummy_topic",
            "subscriptionName": "dummy_sub",
            "dataType": str(DataType.UNDEFINED),
            "accessRights": str(AccessRights.MANAGE.value),
            "isSessionsEnabled": True,
            "cardinality": str(Cardinality.ONE.value)
        })

    def test_service_bus_topic_output_valid_creation(self):
        output = ServiceBusTopicOutput(name="res", connection="dummy_conn",
                                       topic_name="dummy_topic",
                                       subscription_name="dummy_sub",
                                       data_type=DataType.UNDEFINED,
                                       access_rights=AccessRights.MANAGE)

        self.assertEqual(output.get_binding_name(), "serviceBus")
        self.assertEqual(output.get_dict_repr(), {
            "type": "serviceBus",
            "direction": str(BindingDirection.OUT),
            "name": "res",
            "dataType": str(DataType.UNDEFINED),
            "connection": "dummy_conn",
            "topicName": "dummy_topic",
            "subscriptionName": "dummy_sub",
            "accessRights": str(AccessRights.MANAGE.value)
        })
