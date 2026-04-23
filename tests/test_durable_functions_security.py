# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Security tests for durable functions deserialization.

These tests verify that the security fix for arbitrary code execution
via malicious JSON payloads is working correctly.
"""

import unittest
import json
import os
import sys
import tempfile

from azure.functions.durable_functions import ActivityTriggerConverter
from azure.functions.meta import Datum
from azure.functions._cosmosdb import Document
from azure.functions._sql import SqlRow
from azure.functions._mysql import MySqlRow


class TestDurableFunctionsSecurityFix(unittest.TestCase):
    """Test that the security vulnerability CVE fix is effective."""

    def test_legitimate_cosmosdb_document_deserialization_works(self):
        """Verify that legitimate Document deserialization still works."""
        payload = {
            '__module__': 'azure.functions._cosmosdb',
            '__class__': 'Document',
            '__data__': '{"id": "123", "name": "test"}'
        }
        datum = Datum(value=json.dumps(payload), type='json')

        result = ActivityTriggerConverter.decode(datum, trigger_metadata={})

        self.assertIsInstance(result, Document)
        self.assertEqual(result['id'], '123')
        self.assertEqual(result['name'], 'test')

    def test_legitimate_sql_row_deserialization_works(self):
        """Verify that legitimate SqlRow deserialization still works."""
        payload = {
            '__module__': 'azure.functions._sql',
            '__class__': 'SqlRow',
            '__data__': '{"column1": "value1", "column2": "value2"}'
        }
        datum = Datum(value=json.dumps(payload), type='json')

        result = ActivityTriggerConverter.decode(datum, trigger_metadata={})

        self.assertIsInstance(result, SqlRow)
        self.assertEqual(result['column1'], 'value1')
        self.assertEqual(result['column2'], 'value2')

    def test_legitimate_mysql_row_deserialization_works(self):
        """Verify that legitimate MySqlRow deserialization still works."""
        payload = {
            '__module__': 'azure.functions._mysql',
            '__class__': 'MySqlRow',
            '__data__': '{"field1": "data1", "field2": "data2"}'
        }
        datum = Datum(value=json.dumps(payload), type='json')

        result = ActivityTriggerConverter.decode(datum, trigger_metadata={})

        self.assertIsInstance(result, MySqlRow)
        self.assertEqual(result['field1'], 'data1')
        self.assertEqual(result['field2'], 'data2')

    def test_arbitrary_module_import_blocked(self):
        """
        SECURITY TEST: Verify that arbitrary module imports are blocked.

        This test creates a malicious module and attempts to import it
        via the deserialization function. The import should be blocked
        by the allowlist before the module's code can execute.
        """
        # Create a temporary malicious module
        tmpdir = tempfile.mkdtemp()
        marker_file = os.path.join(tmpdir, 'malicious_code_executed.txt')
        evil_module_path = os.path.join(tmpdir, 'evil_module.py')

        # Write malicious module with code that executes on import
        with open(evil_module_path, 'w') as f:
            f.write(f'''
# Malicious code that runs on module import
with open(r"{marker_file}", "w") as f:
    f.write("MALICIOUS CODE EXECUTED")

class EvilClass:
    @classmethod
    def from_json(cls, data):
        return cls()
''')

        # Add temp directory to sys.path to make module importable
        sys.path.insert(0, tmpdir)

        try:
            # Attempt to deserialize with malicious module
            payload = {
                '__module__': 'evil_module',
                '__class__': 'EvilClass',
                '__data__': '{}'
            }
            datum = Datum(value=json.dumps(payload), type='json')

            # This should raise a ValueError due to allowlist
            with self.assertRaises(ValueError) as cm:
                ActivityTriggerConverter.decode(datum, trigger_metadata={})

            # The error is wrapped by ActivityTriggerConverter, check the cause
            self.assertIsNotNone(cm.exception.__cause__)
            cause_msg = str(cm.exception.__cause__)
            self.assertIn('evil_module', cause_msg)
            self.assertIn('not allowed', cause_msg.lower())

            # CRITICAL: Verify the malicious code did NOT execute
            self.assertFalse(
                os.path.exists(marker_file),
                "SECURITY FAILURE: Malicious code executed during module import!"
            )

        finally:
            # Clean up
            sys.path.remove(tmpdir)
            if os.path.exists(evil_module_path):
                os.remove(evil_module_path)
            if os.path.exists(marker_file):
                os.remove(marker_file)
            os.rmdir(tmpdir)

    def test_unauthorized_class_from_allowed_module_blocked(self):
        """SECURITY TEST: Verify that unauthorized classes from allowed modules are blocked."""
        # Try to deserialize a class that doesn't exist in the allowlist
        payload = {
            '__module__': 'azure.functions._cosmosdb',
            '__class__': 'FakeClass',  # Not in allowlist
            '__data__': '{}'
        }
        datum = Datum(value=json.dumps(payload), type='json')

        with self.assertRaises(ValueError) as cm:
            ActivityTriggerConverter.decode(datum, trigger_metadata={})

        # Check the wrapped exception cause
        self.assertIsNotNone(cm.exception.__cause__)
        cause_msg = str(cm.exception.__cause__)
        self.assertIn('FakeClass', cause_msg)
        self.assertIn('not allowed', cause_msg.lower())

    def test_builtin_module_blocked(self):
        """SECURITY TEST: Verify that built-in dangerous modules are blocked."""
        # Attempt to import built-in modules that could be dangerous
        dangerous_payloads = [
            {
                '__module__': 'os',
                '__class__': 'system',
                '__data__': 'echo pwned'
            },
            {
                '__module__': 'subprocess',
                '__class__': 'Popen',
                '__data__': '{}'
            },
            {
                '__module__': '__builtin__',
                '__class__': 'eval',
                '__data__': 'print("pwned")'
            }
        ]

        for payload in dangerous_payloads:
            datum = Datum(value=json.dumps(payload), type='json')

            with self.assertRaises(ValueError) as cm:
                ActivityTriggerConverter.decode(datum, trigger_metadata={})

            # Check the wrapped exception cause
            self.assertIsNotNone(cm.exception.__cause__)
            self.assertIn('not allowed', str(cm.exception.__cause__).lower())

    def test_nested_malicious_object_blocked(self):
        """
        SECURITY TEST: Verify that nested malicious objects are also blocked.

        The object_hook is called for every nested object in the JSON,
        so we need to ensure malicious payloads can't be smuggled in
        nested structures.
        """
        payload = {
            'legitimate_data': 'some value',
            'nested_attack': {
                '__module__': 'os',
                '__class__': 'system',
                '__data__': 'echo pwned'
            }
        }
        datum = Datum(value=json.dumps(payload), type='json')

        with self.assertRaises(ValueError) as cm:
            ActivityTriggerConverter.decode(datum, trigger_metadata={})

        # Check the wrapped exception cause
        self.assertIsNotNone(cm.exception.__cause__)
        self.assertIn('not allowed', str(cm.exception.__cause__).lower())

    def test_nested_legitimate_object_works(self):
        """Verify that nested legitimate objects still work correctly."""
        payload = {
            'normal_data': 'value',
            'nested_document': {
                '__module__': 'azure.functions._cosmosdb',
                '__class__': 'Document',
                '__data__': '{"nested": "data"}'
            }
        }
        datum = Datum(value=json.dumps(payload), type='json')

        result = ActivityTriggerConverter.decode(datum, trigger_metadata={})

        self.assertEqual(result['normal_data'], 'value')
        self.assertIsInstance(result['nested_document'], Document)
        self.assertEqual(result['nested_document']['nested'], 'data')

    def test_allowlist_comprehensiveness(self):
        """
        Verify that the allowlist includes all expected legitimate classes
        and only those classes.
        """
        from azure.functions._durable_functions import _SAFE_DESERIALIZATION_ALLOWLIST

        # Verify expected modules are present
        self.assertIn('azure.functions._cosmosdb', _SAFE_DESERIALIZATION_ALLOWLIST)
        self.assertIn('azure.functions._sql', _SAFE_DESERIALIZATION_ALLOWLIST)
        self.assertIn('azure.functions._mysql', _SAFE_DESERIALIZATION_ALLOWLIST)

        # Verify expected classes are present
        self.assertIn('Document', _SAFE_DESERIALIZATION_ALLOWLIST['azure.functions._cosmosdb'])
        self.assertIn('SqlRow', _SAFE_DESERIALIZATION_ALLOWLIST['azure.functions._sql'])
        self.assertIn('MySqlRow', _SAFE_DESERIALIZATION_ALLOWLIST['azure.functions._mysql'])

        # Verify no unexpected modules or classes
        expected_modules = {
            'azure.functions._cosmosdb',
            'azure.functions._sql',
            'azure.functions._mysql'
        }
        self.assertEqual(set(_SAFE_DESERIALIZATION_ALLOWLIST.keys()), expected_modules)
