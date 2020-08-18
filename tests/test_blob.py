# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Dict, Any
import unittest

import azure.functions as func
import azure.functions.blob as afb
from azure.functions.meta import Datum
from azure.functions.blob import InputStream


class TestBlob(unittest.TestCase):
    def test_blob_input_type(self):
        check_input_type = afb.BlobConverter.check_input_type_annotation
        self.assertTrue(check_input_type(str))
        self.assertTrue(check_input_type(bytes))
        self.assertTrue(check_input_type(InputStream))
        self.assertFalse(check_input_type(bytearray))

    def test_blob_input_none(self):
        result: func.DocumentList = afb.BlobConverter.decode(
            data=None, trigger_metadata=None)
        self.assertIsNone(result)

    def test_blob_input_string_no_metadata(self):
        datum: Datum = Datum(value='string_content', type='string')
        result: InputStream = afb.BlobConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)

        # Verify result metadata
        self.assertIsInstance(result, InputStream)
        self.assertIsNone(result.name)
        self.assertIsNone(result.length)
        self.assertIsNone(result.uri)
        self.assertTrue(result.readable())
        self.assertFalse(result.seekable())
        self.assertFalse(result.writable())

        # Verify result content
        content: bytes = result.read()
        self.assertEqual(content, b'string_content')

    def test_blob_input_bytes_no_metadata(self):
        datum: Datum = Datum(value=b'bytes_content', type='bytes')
        result: InputStream = afb.BlobConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)

        # Verify result metadata
        self.assertIsInstance(result, InputStream)
        self.assertIsNone(result.name)
        self.assertIsNone(result.length)
        self.assertIsNone(result.uri)
        self.assertTrue(result.readable())
        self.assertFalse(result.seekable())
        self.assertFalse(result.writable())

        # Verify result content
        content: bytes = result.read()
        self.assertEqual(content, b'bytes_content')

    def test_blob_input_with_metadata(self):
        datum: Datum = Datum(value=b'blob_content', type='bytes')
        metadata: Dict[str, Any] = {
            'Properties': Datum('{"Length": "12"}', 'json'),
            'BlobTrigger': Datum('blob_trigger_name', 'string'),
            'Uri': Datum('https://test.io/blob_trigger', 'string')
        }
        result: InputStream = afb.BlobConverter.decode(
            data=datum, trigger_metadata=metadata)

        # Verify result metadata
        self.assertIsInstance(result, InputStream)
        self.assertEqual(result.name, 'blob_trigger_name')
        self.assertEqual(result.length, len(b'blob_content'))
        self.assertEqual(result.uri, 'https://test.io/blob_trigger')

    def test_blob_incomplete_read(self):
        datum: Datum = Datum(value=b'blob_content', type='bytes')
        result: InputStream = afb.BlobConverter.decode(
            data=datum, trigger_metadata=None)

        self.assertEqual(result.read(size=3), b'blo')

    def test_blob_output_custom_output_content(self):
        class CustomOutput:
            def read(self) -> bytes:
                return b'custom_output_content'

        # Try encoding a custom instance as an output return
        out = CustomOutput()
        result: Datum = afb.BlobConverter.encode(obj=out, expected_type=None)
        self.assertEqual(result.value, b'custom_output_content')
        self.assertEqual(result.type, 'bytes')

    def test_blob_output_custom_output_without_read_method(self):
        class CustomOutput:
            def _read(self) -> bytes:
                return b'should_not_be_called'

        # Try encoding a custom instance without read() method
        # This should raise an error when an unknown output is returned
        out = CustomOutput()
        with self.assertRaises(NotImplementedError):
            afb.BlobConverter.encode(obj=out, expected_type=None)

    def test_blob_output_string(self):
        out: str = 'blob_output_string'
        result: Datum = afb.BlobConverter.encode(obj=out, expected_type=None)
        self.assertEqual(result.value, 'blob_output_string')
        self.assertEqual(result.type, 'string')

    def test_blob_output_bytes(self):
        out: bytes = b'blob_output_bytes'
        result: Datum = afb.BlobConverter.encode(obj=out, expected_type=None)
        self.assertEqual(result.value, b'blob_output_bytes')
        self.assertEqual(result.type, 'bytes')

    def test_blob_output_type(self):
        check_output_type = afb.BlobConverter.check_output_type_annotation
        self.assertTrue(check_output_type(str))
        self.assertTrue(check_output_type(bytes))
        self.assertTrue(check_output_type(bytearray))
        self.assertTrue(check_output_type(InputStream))

    def test_blob_output_custom_type(self):
        class CustomOutput:
            def read(self) -> Datum:
                return Datum(b'custom_output_content', 'types')

        check_output_type = afb.BlobConverter.check_output_type_annotation
        self.assertTrue(check_output_type(CustomOutput))
