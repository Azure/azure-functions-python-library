# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import json

from azure.functions.durable_functions import (
    OrchestrationTriggerConverter,
    EnitityTriggerConverter,
    ActivityTriggerConverter,
    DurableClientConverter
)
from azure.functions._durable_functions import (
    OrchestrationContext,
    EntityContext
)
from azure.functions.meta import Datum

CONTEXT_CLASSES = [OrchestrationContext, EntityContext]
CONVERTERS = [OrchestrationTriggerConverter, EnitityTriggerConverter]


class TestDurableFunctions(unittest.TestCase):
    def test_context_string_body(self):
        body = '{ "name": "great function" }'
        for ctx in CONTEXT_CLASSES:
            context = ctx(body)
            self.assertIsNotNone(getattr(context, 'body', None))

            content = json.loads(context.body)
            self.assertEqual(content.get('name'), 'great function')

    def test_context_string_cast(self):
        body = '{ "name": "great function" }'
        for ctx in CONTEXT_CLASSES:
            context = ctx(body)
            self.assertEqual(str(context), body)

            content = json.loads(str(context))
            self.assertEqual(content.get('name'), 'great function')

    def test_context_bytes_body(self):
        body = '{ "name": "great function" }'.encode('utf-8')
        for ctx in CONTEXT_CLASSES:
            context = ctx(body)
            self.assertIsNotNone(getattr(context, 'body', None))

            content = json.loads(context.body)
            self.assertEqual(content.get('name'), 'great function')

    def test_context_bytes_cast(self):
        # TODO: this is just like the test above
        # (test_orchestration_context_bytes_body)
        body = '{ "name": "great function" }'.encode('utf-8')
        for ctx in CONTEXT_CLASSES:
            context = ctx(body)
            self.assertIsNotNone(getattr(context, 'body', None))

            content = json.loads(context.body)
            self.assertEqual(content.get('name'), 'great function')

    def test_trigger_converter(self):
        datum = Datum(value='{ "name": "great function" }',
                      type=str)
        for converter in CONVERTERS:
            otc = converter.decode(datum, trigger_metadata=None)
            content = json.loads(otc.body)
            self.assertEqual(content.get('name'), 'great function')

    def test_trigger_converter_type(self):
        datum = Datum(value='{ "name": "great function" }'.encode('utf-8'),
                      type=bytes)
        for converter in CONVERTERS:
            otc = converter.decode(datum, trigger_metadata=None)
            content = json.loads(otc.body)
            self.assertEqual(content.get('name'), 'great function')

    def test_trigger_check_good_annotation(self):

        for converter, ctx in zip(CONVERTERS, CONTEXT_CLASSES):
            self.assertTrue(
                converter.check_input_type_annotation(ctx)
            )

    def test_trigger_check_bad_annotation(self):
        for dt in (str, bytes, int):
            for converter in CONVERTERS:
                self.assertFalse(
                    converter.check_input_type_annotation(dt)
                )

    def test_trigger_has_implicit_return(self):
        for converter in CONVERTERS:
            self.assertTrue(
                converter.has_implicit_output()
            )

    def test_activity_trigger_inputs(self):
        # Activity Trigger only accept string type from durable extensions
        # It will be JSON deserialized into expected data type
        data = [
            {
                'input': Datum('sample', 'string'),
                'expected_value': 'sample',
                'expected_type': str
            },
            {
                'input': Datum('123', 'string'),
                'expected_value': 123,
                'expected_type': int
            },
            {
                'input': Datum('1234.56', 'string'),
                'expected_value': 1234.56,
                'expected_type': float
            },
            {
                'input': Datum('[ "do", "re", "mi" ]', 'string'),
                'expected_value': ["do", "re", "mi"],
                'expected_type': list
            },
            {
                'input': Datum('{ "number": "42" }', 'string'),
                'expected_value': {"number": "42"},
                'expected_type': dict
            }
        ]

        for datum in data:
            decoded = ActivityTriggerConverter.decode(
                data=datum['input'],
                trigger_metadata=None)
            self.assertEqual(decoded, datum['expected_value'])
            self.assertEqual(type(decoded), datum['expected_type'])

    def test_activity_trigger_encode(self):
        # Activity Trigger allow any JSON serializable as outputs
        # The return value will be carried back to the Orchestrator function
        data = [
            {
                'output': str('sample'),
                'expected_value': Datum('"sample"', 'json'),
            },
            {
                'output': int(123),
                'expected_value': Datum('123', 'json'),
            },
            {
                'output': float(1234.56),
                'expected_value': Datum('1234.56', 'json')
            },
            {
                'output': list(["do", "re", "mi"]),
                'expected_value': Datum('["do", "re", "mi"]', 'json')
            },
            {
                'output': dict({"number": "42"}),
                'expected_value': Datum('{"number": "42"}', 'json')
            }
        ]

        for datum in data:
            encoded = ActivityTriggerConverter.encode(
                obj=datum['output'],
                expected_type=type(datum['output']))
            self.assertEqual(encoded, datum['expected_value'])

    def test_activity_trigger_decode(self):
        # Activity Trigger allow inputs to be any JSON serializables
        # The input values to the trigger should be passed into arguments
        data = [
            {
                'input': Datum('sample_string', 'string'),
                'expected_value': str('sample_string')
            },
            {
                'input': Datum('"sample_json_string"', 'json'),
                'expected_value': str('sample_json_string')
            },
            {
                'input': Datum('{ "invalid": "json"', 'json'),
                'expected_value': str('{ "invalid": "json"')
            },
            {
                'input': Datum('true', 'json'),
                'expected_value': bool(True),
            },
            {
                'input': Datum('123', 'json'),
                'expected_value': int(123),
            },
            {
                'input': Datum('1234.56', 'json'),
                'expected_value': float(1234.56)
            },
            {
                'input': Datum('["do", "re", "mi"]', 'json'),
                'expected_value': list(["do", "re", "mi"])
            },
            {
                'input': Datum('{"number": "42"}', 'json'),
                'expected_value': dict({"number": "42"})
            }
        ]

        for datum in data:
            decoded = ActivityTriggerConverter.decode(
                data=datum['input'],
                trigger_metadata=None)
            self.assertEqual(decoded, datum['expected_value'])

    def test_activity_trigger_has_implicit_return(self):
        self.assertTrue(
            ActivityTriggerConverter.has_implicit_output()
        )

    def test_durable_client_no_implicit_return(self):
        self.assertFalse(
            DurableClientConverter.has_implicit_output()
        )

    def test_enitity_trigger_check_output_type_annotation(self):
        self.assertTrue(
            EnitityTriggerConverter.check_output_type_annotation(pytype=None)
        )

    def test_activity_trigger_converter_decode_no_implementation_exception(
            self):
        is_exception_raised = False
        datum = Datum(value=b"dummy", type="bytes")
        # when
        try:
            ActivityTriggerConverter.decode(data=datum, trigger_metadata=None)
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)

    def test_enitity_trigger_converter_encode(self):

        data = '{"dummy_key": "dummy_value"}'

        result = EnitityTriggerConverter.encode(
            obj=data, expected_type=None)

        self.assertEqual(result.type, "json")
        self.assertEqual(result.python_value, {'dummy_key': 'dummy_value'})
