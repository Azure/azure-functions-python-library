# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
import azure.functions as func
from azure.functions.meta import Datum
from azure.functions.mcp import MCPToolTriggerConverter


class TestMCPToolTriggerConverter(unittest.TestCase):
    """Unit tests for MCPToolTriggerConverter"""

    def test_check_input_type_annotation_valid_types(self):
        self.assertTrue(MCPToolTriggerConverter.check_input_type_annotation(str))
        self.assertTrue(MCPToolTriggerConverter.check_input_type_annotation(dict))
        self.assertTrue(MCPToolTriggerConverter.check_input_type_annotation(bytes))
        self.assertTrue(MCPToolTriggerConverter.check_input_type_annotation(func.MCPToolContext))

    def test_check_input_type_annotation_invalid_type(self):
        with self.assertRaises(TypeError):
            MCPToolTriggerConverter.check_input_type_annotation(123)  # not a type

        class Dummy:
            pass
        self.assertFalse(MCPToolTriggerConverter.check_input_type_annotation(Dummy))

    def test_has_implicit_output(self):
        self.assertTrue(MCPToolTriggerConverter.has_implicit_output())

    def test_decode_json(self):
        data = Datum(type='json', value={'foo': 'bar'})
        result = MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, {'foo': 'bar'})

    def test_decode_string(self):
        data = Datum(type='string', value='hello')
        result = MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, 'hello')

    def test_decode_bytes(self):
        data = Datum(type='bytes', value=b'data')
        result = MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, b'data')

    def test_decode_other_without_python_value(self):
        data = Datum(type='other', value='fallback')
        result = MCPToolTriggerConverter.decode(data, trigger_metadata={})
        self.assertEqual(result, 'fallback')

    def test_encode_none(self):
        result = MCPToolTriggerConverter.encode(None)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '')

    def test_encode_string(self):
        result = MCPToolTriggerConverter.encode('hello')
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, 'hello')

    def test_encode_bytes(self):
        result = MCPToolTriggerConverter.encode(b'\x00\x01')
        self.assertEqual(result.type, 'bytes')
        self.assertEqual(result.value, b'\x00\x01')

    def test_encode_bytearray(self):
        result = MCPToolTriggerConverter.encode(bytearray(b'\x01\x02'))
        self.assertEqual(result.type, 'bytes')
        self.assertEqual(result.value, b'\x01\x02')

    def test_encode_other_type(self):
        result = MCPToolTriggerConverter.encode(42)
        self.assertEqual(result.type, 'string')
        self.assertEqual(result.value, '42')

        result = MCPToolTriggerConverter.encode({'a': 1})
        self.assertEqual(result.type, 'string')
        self.assertIn("'a'", result.value)
