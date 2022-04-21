#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import EVENT_HUB_TRIGGER, EVENT_HUB
from azure.functions.decorators.core import BindingDirection, Cardinality, \
    DataType
from azure.functions.decorators.eventhub import EventHubTrigger, EventHubOutput


class TestEventHub(unittest.TestCase):
    def test_event_hub_trigger_valid_creation(self):
        trigger = EventHubTrigger(name="req",
                                  connection="dummy_connection",
                                  event_hub_name="dummy_event_hub",
                                  cardinality=Cardinality.ONE,
                                  consumer_group="dummy_group",
                                  data_type=DataType.UNDEFINED,
                                  dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "eventHubTrigger")
        self.assertEqual(trigger.get_dict_repr(),
                         {"cardinality": Cardinality.ONE,
                          "connection": "dummy_connection",
                          "consumerGroup": "dummy_group",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          'dummyField': 'dummy',
                          "eventHubName": "dummy_event_hub",
                          "name": "req",
                          "type": EVENT_HUB_TRIGGER})

    def test_event_hub_output_valid_creation(self):
        output = EventHubOutput(name="res",
                                event_hub_name="dummy_event_hub",
                                connection="dummy_connection",
                                data_type=DataType.UNDEFINED,
                                dummy_field="dummy")

        self.assertEqual(output.get_binding_name(), "eventHub")
        self.assertEqual(output.get_dict_repr(),
                         {'connection': 'dummy_connection',
                          'dataType': DataType.UNDEFINED,
                          'direction': BindingDirection.OUT,
                          'dummyField': 'dummy',
                          'eventHubName': 'dummy_event_hub',
                          'name': 'res',
                          'type': EVENT_HUB})
