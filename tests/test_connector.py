# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
import json
import azure.functions as func
from azure.functions.meta import Datum
from azure.functions.connectors import ConnectorTriggerConverter


class TestConnectorTriggerConverter(unittest.TestCase):
    """Unit tests for ConnectorTriggerConverter"""

    def test_check_input_type_annotation_valid_types(self):
        self.assertTrue(ConnectorTriggerConverter.check_input_type_annotation(str))
        self.assertTrue(ConnectorTriggerConverter.check_input_type_annotation(dict))
        self.assertTrue(ConnectorTriggerConverter.check_input_type_annotation(bytes))

    def test_check_input_type_annotation_invalid_type(self):
        with self.assertRaises(TypeError):
            ConnectorTriggerConverter.check_input_type_annotation(123)  # not a type

        class Dummy:
            pass
        self.assertFalse(ConnectorTriggerConverter.check_input_type_annotation(Dummy))

    def test_has_implicit_output(self):
        self.assertTrue(ConnectorTriggerConverter.has_implicit_output())

    def test_decode_json(self):
        data = Datum(type='json', value={'foo': 'bar', 'count': 42})
        result = ConnectorTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, {'foo': 'bar', 'count': 42})

    def test_decode_string(self):
        data = Datum(type='string', value='hello connector')
        result = ConnectorTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, 'hello connector')

    def test_decode_bytes(self):
        data = Datum(type='bytes', value=b'binary data')
        result = ConnectorTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, b'binary data')

    def test_decode_other_without_python_value(self):
        data = Datum(type='other', value='fallback value')
        result = ConnectorTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, 'fallback value')

    def test_decode_other_with_python_value(self):
        class MockDatum:
            type = 'custom'
            value = 'original'
            python_value = 'python version'

        data = MockDatum()
        result = ConnectorTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, 'python version')

    def test_encode_none(self):
        result = ConnectorTriggerConverter.encode(None)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '')

    def test_encode_string(self):
        result = ConnectorTriggerConverter.encode('hello connector')
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, 'hello connector')

    def test_encode_bytes(self):
        result = ConnectorTriggerConverter.encode(b'\x00\x01\x02')
        self.assertEqual(result.type, 'bytes')
        self.assertEqual(result.value, b'\x00\x01\x02')

    def test_encode_bytearray(self):
        result = ConnectorTriggerConverter.encode(bytearray(b'\x01\x02\x03'))
        self.assertEqual(result.type, 'bytes')
        self.assertEqual(result.value, b'\x01\x02\x03')

    def test_encode_dict(self):
        input_dict = {'status': 'success', 'data': [1, 2, 3]}
        result = ConnectorTriggerConverter.encode(input_dict)
        self.assertEqual(result.type, 'string')
        # Parse the JSON to verify it's correct
        parsed = json.loads(result.value)
        self.assertEqual(parsed, input_dict)

    def test_encode_dict_with_nested_data(self):
        input_dict = {
            'name': 'test',
            'nested': {'key': 'value'},
            'list': [1, 2, 3]
        }
        result = ConnectorTriggerConverter.encode(input_dict)
        self.assertEqual(result.type, 'string')
        parsed = json.loads(result.value)
        self.assertEqual(parsed, input_dict)

    def test_encode_other_type(self):
        result = ConnectorTriggerConverter.encode(42)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '42')

        result = ConnectorTriggerConverter.encode(True)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, 'True')


class TestConnectorDecoratorIntegration(unittest.TestCase):
    """Integration tests for the connector trigger decorator"""

    def test_decorator_creates_function_with_trigger(self):
        app = func.FunctionApp()

        @app.connector_trigger(arg_name="payload")
        def connector_function(payload):
            return f"Received: {payload}"

        # Get the built function
        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)

        built_func = funcs[0]
        self.assertIsNotNone(built_func.get_trigger())
        self.assertEqual(built_func.get_trigger().type, 'connectorTrigger')

    def test_decorator_with_data_type(self):
        app = func.FunctionApp()

        @app.connector_trigger(
            arg_name="context",
            data_type=func.DataType.STRING
        )
        def connector_with_datatype(context):
            return context

        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)

        built_func = funcs[0]
        trigger = built_func.get_trigger()
        self.assertIsNotNone(trigger)
        self.assertEqual(trigger.get_dict_repr()['dataType'], func.DataType.STRING)

    def test_decorator_with_kwargs(self):
        app = func.FunctionApp()

        @app.connector_trigger(
            arg_name="data",
            custom_field="custom_value",
            another_property=123
        )
        def connector_with_kwargs(data):
            return data

        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)

        built_func = funcs[0]
        bindings = built_func.get_bindings()
        self.assertEqual(len(bindings), 1)

        trigger_dict = bindings[0].get_dict_repr()
        self.assertEqual(trigger_dict['type'], 'connectorTrigger')
        self.assertEqual(trigger_dict['customField'], 'custom_value')
        self.assertEqual(trigger_dict['anotherProperty'], 123)

    def test_decorator_poll_serializes_all_fields(self):
        for mode in (func.DeliveryMode.POLL, "Poll", "poll", "POLL"):
            for cardinality in (func.Cardinality.ONE, "one",
                                func.Cardinality.MANY, "many"):
                with self.subTest(mode=mode, cardinality=cardinality):
                    app = func.FunctionApp()

                    @app.connector_trigger(
                        arg_name="payload",
                        delivery_mode=mode,
                        connection="ConnectorNamespace",
                        trigger_config_name="%OnNewEmailTriggerConfigName%",
                        cardinality=cardinality,
                        max_batch_size=1,
                        max_concurrent_calls=1,
                        target_pending_event_threshold=16,
                        data_type="string",
                        custom_field="custom",
                    )
                    def connector_function(payload):
                        return payload

                    binding = json.loads(
                        app.get_functions()[0].get_function_json())['bindings'][0]
                    self.assertEqual(binding, {
                        "type": "connectorTrigger",
                        "direction": "IN",
                        "name": "payload",
                        "deliveryMode": "Poll",
                        "connection": "ConnectorNamespace",
                        "triggerConfigName": "%OnNewEmailTriggerConfigName%",
                        "cardinality": str(cardinality).upper(),
                        "maxBatchSize": 1,
                        "maxConcurrentCalls": 1,
                        "targetPendingEventThreshold": 16,
                        "dataType": "STRING",
                        "customField": "custom",
                    })

    def test_decorator_webhook_and_default_require_no_poll_fields(self):
        for mode in (None, func.DeliveryMode.WEBHOOK, "Webhook", "webhook"):
            with self.subTest(mode=mode):
                app = func.FunctionApp()

                @app.connector_trigger(arg_name="payload", delivery_mode=mode)
                def connector_function(payload):
                    return payload

                binding = json.loads(
                    app.get_functions()[0].get_function_json())['bindings'][0]
                expected = {
                    "type": "connectorTrigger",
                    "direction": "IN",
                    "name": "payload",
                }
                if mode is not None:
                    expected["deliveryMode"] = "Webhook"
                self.assertEqual(binding, expected)

    def test_decorator_poll_requires_each_field(self):
        required = {
            "connection": "ConnectorNamespace",
            "trigger_config_name": "config",
            "max_batch_size": 1,
            "max_concurrent_calls": 1,
        }
        for mode in (func.DeliveryMode.POLL, "Poll"):
            for field in required:
                with self.subTest(mode=mode, field=field):
                    app = func.FunctionApp()
                    params = dict(required)
                    del params[field]
                    with self.assertRaisesRegex(ValueError, field):
                        @app.connector_trigger(arg_name="payload",
                                               delivery_mode=mode, **params)
                        def connector_function(payload):
                            return payload

    def test_decorator_invalid_enums(self):
        for params, enum_name in (({"delivery_mode": "invalid"}, "DeliveryMode"),
                                  ({"cardinality": "invalid"}, "Cardinality")):
            with self.subTest(params=params):
                app = func.FunctionApp()
                with self.assertRaisesRegex(KeyError, enum_name):
                    @app.connector_trigger(arg_name="payload", **params)
                    def connector_function(payload):
                        return payload

    def test_decorator_preserves_positional_data_type(self):
        app = func.FunctionApp()

        @app.connector_trigger("payload", func.DataType.STRING)
        def connector_function(payload):
            return payload

        trigger = app.get_functions()[0].get_trigger()
        self.assertEqual(trigger.get_dict_repr()['dataType'], func.DataType.STRING)

    def test_decorator_poll_cardinality_is_optional(self):
        app = func.FunctionApp()

        @app.connector_trigger(
            arg_name="payload", delivery_mode=func.DeliveryMode.POLL,
            connection="ConnectorNamespace", trigger_config_name="config",
            max_batch_size=1, max_concurrent_calls=1,
        )
        def connector_function(payload):
            return payload

        binding = app.get_functions()[0].get_trigger().get_dict_repr()
        self.assertNotIn("cardinality", binding)
        self.assertNotIn("isBatched", binding)
        self.assertNotIn("targetPendingEventThreshold", binding)
