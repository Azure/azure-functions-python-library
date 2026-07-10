# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
import json
import azure.functions as func
from azure.functions.meta import Datum
from azure.functions.mcp import (_MCPToolTriggerConverter,
                                 _MCPPromptTriggerConverter,
                                 PromptInvocationContext)


class TestMCPToolTriggerConverter(unittest.TestCase):
    """Unit tests for _MCPToolTriggerConverter"""

    def test_check_input_type_annotation_valid_types(self):
        self.assertTrue(_MCPToolTriggerConverter.check_input_type_annotation(str))
        self.assertTrue(_MCPToolTriggerConverter.check_input_type_annotation(dict))
        self.assertTrue(_MCPToolTriggerConverter.check_input_type_annotation(bytes))
        self.assertTrue(_MCPToolTriggerConverter.check_input_type_annotation(func.MCPToolContext))

    def test_check_input_type_annotation_invalid_type(self):
        with self.assertRaises(TypeError):
            _MCPToolTriggerConverter.check_input_type_annotation(123)  # not a type

        class Dummy:
            pass
        self.assertFalse(_MCPToolTriggerConverter.check_input_type_annotation(Dummy))

    def test_has_implicit_output(self):
        self.assertTrue(_MCPToolTriggerConverter.has_implicit_output())

    def test_decode_json(self):
        data = Datum(type='json', value={'foo': 'bar'})
        result = _MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, {'foo': 'bar'})

    def test_decode_string(self):
        data = Datum(type='string', value='hello')
        result = _MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, 'hello')

    def test_decode_bytes(self):
        data = Datum(type='bytes', value=b'data')
        result = _MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, b'data')

    def test_decode_other_without_python_value(self):
        data = Datum(type='other', value='fallback')
        result = _MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, 'fallback')

    def test_encode_none(self):
        result = _MCPToolTriggerConverter.encode(None)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '')

    def test_encode_string(self):
        result = _MCPToolTriggerConverter.encode('hello')
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, 'hello')

    def test_encode_bytes(self):
        result = _MCPToolTriggerConverter.encode(b'\x00\x01')
        self.assertEqual(result.type, 'bytes')
        self.assertEqual(result.value, b'\x00\x01')

    def test_encode_bytearray(self):
        result = _MCPToolTriggerConverter.encode(bytearray(b'\x01\x02'))
        self.assertEqual(result.type, 'bytes')
        self.assertEqual(result.value, b'\x01\x02')

    def test_encode_other_type(self):
        result = _MCPToolTriggerConverter.encode(42)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '42')

        result = _MCPToolTriggerConverter.encode({'a': 1})
        self.assertEqual(result.type, 'string')
        self.assertIn("'a'", result.value)


class TestPromptInvocationContext(unittest.TestCase):
    """Unit tests for PromptInvocationContext"""

    def test_create_from_dict(self):
        data = {
            'name': 'code_review',
            'arguments': {'code': 'print("hello")', 'language': 'python'},
            'sessionid': 'session-123',
            'transport': {'name': 'http'}
        }
        context = PromptInvocationContext(data)

        self.assertEqual(context.name, 'code_review')
        self.assertEqual(context.arguments, {'code': 'print("hello")', 'language': 'python'})
        self.assertEqual(context.sessionid, 'session-123')
        self.assertEqual(context.transport, {'name': 'http'})

    def test_create_from_json_string(self):
        data = json.dumps({
            'name': 'summarize',
            'arguments': {'text': 'Hello world'},
            'sessionid': None
        })
        context = PromptInvocationContext(data)

        self.assertEqual(context.name, 'summarize')
        self.assertEqual(context.arguments, {'text': 'Hello world'})
        self.assertIsNone(context.sessionid)

    def test_missing_fields_return_defaults(self):
        data = {'name': 'test_prompt'}
        context = PromptInvocationContext(data)

        self.assertEqual(context.name, 'test_prompt')
        self.assertEqual(context.arguments, {})
        self.assertIsNone(context.sessionid)
        self.assertIsNone(context.transport)

    def test_empty_dict(self):
        context = PromptInvocationContext({})

        self.assertEqual(context.name, '')
        self.assertEqual(context.arguments, {})
        self.assertIsNone(context.sessionid)

    def test_arguments_property_access(self):
        data = {
            'name': 'code_review',
            'arguments': {'code': 'def hello(): pass', 'language': 'python'}
        }
        context = PromptInvocationContext(data)

        # Test property access pattern
        code = context.arguments.get('code', '')
        language = context.arguments.get('language', 'unknown')

        self.assertEqual(code, 'def hello(): pass')
        self.assertEqual(language, 'python')

    def test_repr(self):
        data = {'name': 'test', 'arguments': {'a': 'b'}}
        context = PromptInvocationContext(data)
        repr_str = repr(context)

        self.assertIn('test', repr_str)
        self.assertIn('PromptInvocationContext', repr_str)


class TestMCPPromptTriggerConverter(unittest.TestCase):
    """Unit tests for _MCPPromptTriggerConverter"""

    def test_check_input_type_annotation_valid_types(self):
        self.assertTrue(
            _MCPPromptTriggerConverter.check_input_type_annotation(str))
        self.assertTrue(
            _MCPPromptTriggerConverter.check_input_type_annotation(dict))
        self.assertTrue(
            _MCPPromptTriggerConverter.check_input_type_annotation(bytes))
        self.assertTrue(
            _MCPPromptTriggerConverter.check_input_type_annotation(
                PromptInvocationContext))

    def test_check_input_type_annotation_invalid_type(self):
        with self.assertRaises(TypeError):
            _MCPPromptTriggerConverter.check_input_type_annotation(
                123)  # not a type

        class Dummy:
            pass
        self.assertFalse(
            _MCPPromptTriggerConverter.check_input_type_annotation(Dummy))

    def test_has_implicit_output(self):
        self.assertTrue(_MCPPromptTriggerConverter.has_implicit_output())

    def test_decode_json_returns_context(self):
        data = Datum(type='json',
                     value={'name': 'test', 'arguments': {'arg1': 'value1'}})
        result = _MCPPromptTriggerConverter.decode(data, trigger_metadata={})

        self.assertIsInstance(result, PromptInvocationContext)
        self.assertEqual(result.name, 'test')
        self.assertEqual(result.arguments, {'arg1': 'value1'})

    def test_decode_string_returns_context(self):
        json_str = json.dumps(
            {'name': 'code_review', 'arguments': {'code': 'test'}})
        data = Datum(type='string', value=json_str)
        result = _MCPPromptTriggerConverter.decode(data, trigger_metadata={})

        self.assertIsInstance(result, PromptInvocationContext)
        self.assertEqual(result.name, 'code_review')
        self.assertEqual(result.arguments, {'code': 'test'})

    def test_decode_bytes_returns_context(self):
        json_str = json.dumps({'name': 'summarize', 'arguments': {}})
        data = Datum(type='bytes', value=json_str.encode('utf-8'))
        result = _MCPPromptTriggerConverter.decode(data, trigger_metadata={})

        self.assertIsInstance(result, PromptInvocationContext)
        self.assertEqual(result.name, 'summarize')

    def test_encode_none(self):
        result = _MCPPromptTriggerConverter.encode(None)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '')

    def test_encode_string(self):
        result = _MCPPromptTriggerConverter.encode('Please review this code')
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, 'Please review this code')

    def test_encode_bytes(self):
        result = _MCPPromptTriggerConverter.encode(b'\x00\x01')
        self.assertEqual(result.type, 'bytes')
        self.assertEqual(result.value, b'\x00\x01')

    def test_encode_other_type(self):
        result = _MCPPromptTriggerConverter.encode(42)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '42')
