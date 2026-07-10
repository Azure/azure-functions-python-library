#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import CONNECTOR_TRIGGER
from azure.functions.decorators.core import BindingDirection, DataType
from azure.functions.decorators.connectors import ConnectorTrigger


class TestConnectorTrigger(unittest.TestCase):
    def test_connector_trigger_valid_creation(self):
        trigger = ConnectorTrigger(name="payload",
                                   data_type=DataType.UNDEFINED,
                                   dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), CONNECTOR_TRIGGER)
        self.assertEqual(trigger.get_dict_repr(), {
            "type": CONNECTOR_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "payload",
            "dataType": DataType.UNDEFINED
        })

    def test_connector_trigger_minimal_creation(self):
        trigger = ConnectorTrigger(name="req")

        self.assertEqual(trigger.get_binding_name(), "connectorTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "connectorTrigger",
            "direction": BindingDirection.IN,
            "name": "req"
        })

    def test_connector_trigger_with_kwargs(self):
        trigger = ConnectorTrigger(
            name="context",
            data_type=DataType.STRING,
            custom_property="custom_value",
            another_field=123
        )

        self.assertEqual(trigger.get_binding_name(), "connectorTrigger")
        dict_repr = trigger.get_dict_repr()
        self.assertEqual(dict_repr["type"], "connectorTrigger")
        self.assertEqual(dict_repr["name"], "context")
        self.assertEqual(dict_repr["dataType"], DataType.STRING)
        self.assertEqual(dict_repr["customProperty"], "custom_value")
        self.assertEqual(dict_repr["anotherField"], 123)
