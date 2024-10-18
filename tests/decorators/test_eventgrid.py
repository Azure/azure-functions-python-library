#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import EVENT_GRID_TRIGGER, EVENT_GRID
from azure.functions.decorators.core import BindingDirection, \
    DataType
from azure.functions.decorators.eventgrid import (
    EventGridTrigger,
    EventGridOutput)


class TestEventGrid(unittest.TestCase):
    def test_event_grid_trigger_valid_creation(self):
        trigger = EventGridTrigger(name="req",
                                   data_type=DataType.UNDEFINED,
                                   dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "eventGridTrigger")
        self.assertEqual(trigger.get_dict_repr(),
                         {'name': 'req',
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          'dummyField': 'dummy',
                          "type": EVENT_GRID_TRIGGER})

    def test_event_grid_output_valid_creation(self):
        output = EventGridOutput(name="res",
                                 topic_endpoint_uri="dummy_topic_endpoint_uri",
                                 topic_key_setting="dummy_topic_key_setting",
                                 data_type=DataType.UNDEFINED,
                                 dummy_field="dummy")

        self.assertEqual(output.get_binding_name(), "eventGrid")
        self.assertEqual(output.get_dict_repr(),
                         {'dataType': DataType.UNDEFINED,
                             'direction': BindingDirection.OUT,
                             'dummyField': 'dummy',
                             'topicEndpointUri': 'dummy_topic_endpoint_uri',
                             'topicKeySetting': 'dummy_topic_key_setting',
                             'name': 'res',
                             'type': EVENT_GRID})

    def test_event_grid_output_valid_creation_with_connection(self):
        output = EventGridOutput(name="res",
                                 connection="dummy_connection",
                                 data_type=DataType.UNDEFINED,
                                 dummy_field="dummy")

        self.assertEqual(output.connection, "dummy_connection")
        self.assertIsNone(output.topic_endpoint_uri)
        self.assertIsNone(output.topic_key_setting)

    def test_event_grid_output_invalid_creation_with_both(self):
        with self.assertRaises(ValueError) as context:
            EventGridOutput(name="res",
                            connection="dummy_connection",
                            topic_endpoint_uri="dummy_topic_endpoint_uri",
                            topic_key_setting="dummy_topic_key_setting")

        self.assertTrue("Specify either the 'Connection' property or both "
                        "'TopicKeySetting' and 'TopicEndpointUri' properties, "
                        "but not both." in str(context.exception))

    def test_event_grid_output_invalid_creation_with_none(self):
        with self.assertRaises(ValueError) as context:
            EventGridOutput(name="res",
                            data_type=DataType.UNDEFINED,
                            dummy_field="dummy")

        self.assertTrue("Specify either the 'Connection' property or both "
                        "'TopicKeySetting' and 'TopicEndpointUri' properties,"
                        " but not both." in str(context.exception))
