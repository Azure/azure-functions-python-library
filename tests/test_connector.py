# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
import json
import azure.functions as func
from azure.functions.meta import Datum
from azure.functions.connector import (ConnectorTriggerConverter,
                                       ConnectorContext)


class TestConnectorTriggerConverter(unittest.TestCase):
    """Unit tests for ConnectorTriggerConverter"""

    def test_check_input_type_annotation_valid_types(self):
        self.assertTrue(ConnectorTriggerConverter.check_input_type_annotation(str))
        self.assertTrue(ConnectorTriggerConverter.check_input_type_annotation(dict))
        self.assertTrue(ConnectorTriggerConverter.check_input_type_annotation(bytes))
        self.assertTrue(ConnectorTriggerConverter.check_input_type_annotation(ConnectorContext))

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

    def test_connector_context_is_dict_subclass(self):
        # Verify ConnectorContext is a dict subclass
        self.assertTrue(issubclass(ConnectorContext, dict))
        
        # Test that it can be instantiated and used as a dict
        ctx = ConnectorContext({'key': 'value'})
        self.assertEqual(ctx['key'], 'value')


class TestConnectorDecoratorIntegration(unittest.TestCase):
    """Integration tests for the connector trigger decorator"""

    def test_decorator_creates_function_with_trigger(self):
        app = func.FunctionApp()

        @app.generic_connector_trigger(arg_name="payload")
        def connector_function(payload):
            return f"Received: {payload}"

        # Verify the function was decorated
        self.assertIsNotNone(connector_function)
        
        # Check that it has the expected structure
        # The decorator should return a Function object
        self.assertTrue(hasattr(connector_function, 'get_triggers'))

    def test_decorator_with_data_type(self):
        app = func.FunctionApp()

        @app.generic_connector_trigger(
            arg_name="context",
            data_type=func.DataType.STRING
        )
        def connector_with_datatype(context):
            return context

        self.assertIsNotNone(connector_with_datatype)
        self.assertTrue(hasattr(connector_with_datatype, 'get_triggers'))

    def test_decorator_with_kwargs(self):
        app = func.FunctionApp()

        @app.generic_connector_trigger(
            arg_name="data",
            custom_field="custom_value",
            another_property=123
        )
        def connector_with_kwargs(data):
            return data

        self.assertIsNotNone(connector_with_kwargs)
        
        # Verify trigger was added with kwargs
        triggers = connector_with_kwargs.get_triggers()
        self.assertEqual(len(triggers), 1)
        
        trigger_dict = triggers[0].get_dict_repr()
        self.assertEqual(trigger_dict['type'], 'connectorTrigger')
        self.assertEqual(trigger_dict['customField'], 'custom_value')
        self.assertEqual(trigger_dict['anotherProperty'], 123)
