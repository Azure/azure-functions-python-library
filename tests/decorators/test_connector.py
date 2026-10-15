#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

import azure.functions as func
import azure.functions.decorators as decorators
from azure.functions.decorators.constants import CONNECTOR_TRIGGER
from azure.functions.decorators.core import (
    BindingDirection, Cardinality, DataType, DeliveryMode)
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

    def test_delivery_mode_public_exports(self):
        self.assertIs(func.DeliveryMode, DeliveryMode)
        self.assertIs(decorators.DeliveryMode, DeliveryMode)
        self.assertIn("DeliveryMode", func.__all__)
        self.assertIn("DeliveryMode", decorators.__all__)
        self.assertEqual(DeliveryMode.POLL.value, "Poll")
        self.assertEqual(DeliveryMode.WEBHOOK.value, "Webhook")

    def test_connector_trigger_poll_all_fields(self):
        trigger = ConnectorTrigger(
            name="payload",
            delivery_mode=DeliveryMode.POLL,
            connection="ConnectorNamespace",
            trigger_config_name="%OnNewEmailTriggerConfigName%",
            cardinality=Cardinality.MANY,
            max_batch_size=10,
            max_concurrent_calls=1,
            target_pending_event_threshold=16,
            custom_field="custom",
        )

        self.assertEqual(trigger.get_dict_repr(), {
            "type": CONNECTOR_TRIGGER,
            "direction": BindingDirection.IN,
            "name": "payload",
            "deliveryMode": DeliveryMode.POLL,
            "connection": "ConnectorNamespace",
            "triggerConfigName": "%OnNewEmailTriggerConfigName%",
            "cardinality": Cardinality.MANY,
            "maxBatchSize": 10,
            "maxConcurrentCalls": 1,
            "targetPendingEventThreshold": 16,
            "customField": "custom",
        })

    def test_connector_trigger_poll_optional_fields_omitted(self):
        trigger = ConnectorTrigger(
            name="payload", delivery_mode=DeliveryMode.POLL,
            connection="ConnectorNamespace", trigger_config_name="config",
        )
        binding = trigger.get_dict_repr()
        self.assertNotIn("maxBatchSize", binding)
        self.assertNotIn("maxConcurrentCalls", binding)
        self.assertNotIn("cardinality", binding)
        self.assertNotIn("targetPendingEventThreshold", binding)
        self.assertNotIn("isBatched", binding)

    def test_connector_trigger_poll_requires_each_field(self):
        required = {
            "connection": "ConnectorNamespace",
            "trigger_config_name": "config",
        }
        for field in required:
            with self.subTest(field=field):
                params = dict(required)
                params[field] = None
                with self.assertRaisesRegex(ValueError, field):
                    ConnectorTrigger(name="payload",
                                     delivery_mode=DeliveryMode.POLL, **params)

    def test_connector_trigger_poll_reports_all_missing_fields(self):
        with self.assertRaisesRegex(
                ValueError, "connection, trigger_config_name$"):
            ConnectorTrigger(name="payload", delivery_mode=DeliveryMode.POLL)

    def test_connector_trigger_poll_independent_overrides(self):
        for field, value, wire_name in (
                ("max_batch_size", 10, "maxBatchSize"),
                ("max_concurrent_calls", 2, "maxConcurrentCalls")):
            with self.subTest(field=field):
                trigger = ConnectorTrigger(
                    name="payload", delivery_mode="Poll",
                    connection="ConnectorNamespace", trigger_config_name="config",
                    **{field: value},
                )
                self.assertEqual(trigger.get_dict_repr(), {
                    "type": CONNECTOR_TRIGGER,
                    "direction": BindingDirection.IN,
                    "name": "payload",
                    "deliveryMode": DeliveryMode.POLL,
                    "connection": "ConnectorNamespace",
                    "triggerConfigName": "config",
                    wire_name: value,
                })

    def test_connector_trigger_webhook_requires_no_poll_fields(self):
        trigger = ConnectorTrigger(name="payload",
                                   delivery_mode=DeliveryMode.WEBHOOK)
        self.assertEqual(trigger.get_dict_repr(), {
            "type": CONNECTOR_TRIGGER,
            "direction": BindingDirection.IN,
            "name": "payload",
            "deliveryMode": DeliveryMode.WEBHOOK,
        })

    def test_connector_trigger_preserves_positional_data_type(self):
        trigger = ConnectorTrigger("payload", DataType.STRING)
        self.assertEqual(trigger.get_dict_repr()["dataType"], DataType.STRING)

    def test_connector_trigger_preserves_zero_values(self):
        trigger = ConnectorTrigger(
            name="payload", max_batch_size=0, max_concurrent_calls=0,
            target_pending_event_threshold=0,
        )
        binding = trigger.get_dict_repr()
        self.assertEqual(binding["maxBatchSize"], 0)
        self.assertEqual(binding["maxConcurrentCalls"], 0)
        self.assertEqual(binding["targetPendingEventThreshold"], 0)

    def test_connector_trigger_accepts_enum_strings(self):
        for mode in ("Poll", "poll", "POLL"):
            for cardinality in ("one", "ONE", "many", "MANY"):
                with self.subTest(mode=mode, cardinality=cardinality):
                    trigger = ConnectorTrigger(
                        name="payload", delivery_mode=mode,
                        cardinality=cardinality,
                        connection="ConnectorNamespace",
                        trigger_config_name="config",
                        max_batch_size=1, max_concurrent_calls=1,
                    )
                    binding = trigger.get_dict_repr()
                    self.assertIs(binding["deliveryMode"], DeliveryMode.POLL)
                    self.assertIs(binding["cardinality"],
                                  Cardinality[cardinality.upper()])

    def test_connector_trigger_accepts_webhook_strings(self):
        for mode in ("Webhook", "webhook", "WEBHOOK"):
            with self.subTest(mode=mode):
                trigger = ConnectorTrigger(name="payload", delivery_mode=mode)
                self.assertIs(trigger.delivery_mode, DeliveryMode.WEBHOOK)

    def test_connector_trigger_poll_string_requires_fields(self):
        with self.assertRaisesRegex(ValueError, "connection"):
            ConnectorTrigger(name="payload", delivery_mode="Poll")

    def test_connector_trigger_rejects_invalid_enum_strings(self):
        with self.assertRaisesRegex(KeyError, "DeliveryMode"):
            ConnectorTrigger(name="payload", delivery_mode="invalid")
        with self.assertRaisesRegex(KeyError, "Cardinality"):
            ConnectorTrigger(name="payload", cardinality="invalid")
