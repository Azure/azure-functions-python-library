# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import json

from azure.functions.durable_functions import (
    LegacyOrchestrationTriggerConverter,
    LegacyEnitityTriggerConverter,
    LegacyActivityTriggerConverter,
    LegacyDurableClientConverter
)
from azure.functions._durable_functions import (
    OrchestrationContext,
    EntityContext
)
from azure.functions.meta import Datum

CONTEXT_CLASSES = [OrchestrationContext, EntityContext]
CONVERTERS = [LegacyOrchestrationTriggerConverter, LegacyEnitityTriggerConverter]


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
            decoded = LegacyActivityTriggerConverter.decode(
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
            encoded = LegacyActivityTriggerConverter.encode(
                obj=datum['output'],
                expected_type=type(datum['output']))
            self.assertEqual(encoded, datum['expected_value'])

    def test_activity_trigger_encode_failure_exception_has_cause(self):
        class NonEncodable:
            def __init__(self):
                self.value = 'foo'

        data = NonEncodable()

        try:
            LegacyActivityTriggerConverter.encode(data, expected_type=None)
        except ValueError as e:
            self.assertIsNotNone(e.__cause__)
            self.assertIsInstance(e.__cause__, TypeError)

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
            decoded = LegacyActivityTriggerConverter.decode(
                data=datum['input'],
                trigger_metadata=None)
            self.assertEqual(decoded, datum['expected_value'])

    def test_activity_trigger_decode_failure_exception_has_cause(self):
        data = Datum('{"value": "bar"}', 'json')

        try:
            LegacyActivityTriggerConverter.decode(
                data=data,
                trigger_metadata=None)
        except ValueError as e:
            self.assertIsNotNone(e.__cause__)
            self.assertIsInstance(e.__cause__, TypeError)

    def test_activity_trigger_has_implicit_return(self):
        self.assertTrue(
            LegacyActivityTriggerConverter.has_implicit_output()
        )

    def test_durable_client_no_implicit_return(self):
        self.assertFalse(
            LegacyDurableClientConverter.has_implicit_output()
        )

    def test_enitity_trigger_check_output_type_annotation(self):
        self.assertTrue(
            LegacyEnitityTriggerConverter.check_output_type_annotation(pytype=None)
        )

    def test_activity_trigger_converter_decode_no_implementation_exception(
            self):
        is_exception_raised = False
        datum = Datum(value=b"dummy", type="bytes")
        # when
        try:
            LegacyActivityTriggerConverter.decode(data=datum, trigger_metadata=None)
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)

    def test_enitity_trigger_converter_encode(self):

        data = '{"dummy_key": "dummy_value"}'

        result = LegacyEnitityTriggerConverter.encode(
            obj=data, expected_type=None)

        self.assertEqual(result.type, "json")
        self.assertEqual(result.python_value, {'dummy_key': 'dummy_value'})

    def test_durable_client_converter_has_trigger_support(self):
        self.assertFalse(LegacyDurableClientConverter.has_trigger_support())

    def test_durable_client_converter_check_input_type_annotation(self):
        self.assertTrue(LegacyDurableClientConverter.check_input_type_annotation(str))
        self.assertTrue(LegacyDurableClientConverter.check_input_type_annotation(bytes))
        self.assertFalse(LegacyDurableClientConverter.check_input_type_annotation(int))

    def test_durable_client_converter_check_output_type_annotation(self):
        self.assertTrue(LegacyDurableClientConverter.check_output_type_annotation(str))
        self.assertTrue(LegacyDurableClientConverter.check_output_type_annotation(bytes))
        self.assertTrue(LegacyDurableClientConverter.check_output_type_annotation(bytearray))
        self.assertFalse(LegacyDurableClientConverter.check_output_type_annotation(int))

    def test_durable_client_converter_encode(self):
        datum = LegacyDurableClientConverter.encode(obj="hello", expected_type=str)
        self.assertEqual(datum.type, "string")
        self.assertEqual(datum.value, "hello")

        datum = LegacyDurableClientConverter.encode(obj=b"data", expected_type=bytes)
        self.assertEqual(datum.type, "bytes")
        self.assertEqual(datum.value, b"data")

        datum = LegacyDurableClientConverter.encode(obj=None, expected_type=None)
        self.assertIsNone(datum.type)
        self.assertIsNone(datum.value)

        datum = LegacyDurableClientConverter.encode(obj={"a": 1}, expected_type=dict)
        self.assertEqual(datum.type, "dict")
        self.assertEqual(datum.value, {"a": 1})

        datum = LegacyDurableClientConverter.encode(obj=[1, 2], expected_type=list)
        self.assertEqual(datum.type, "list")
        self.assertEqual(datum.value, [1, 2])

        datum = LegacyDurableClientConverter.encode(obj=42, expected_type=int)
        self.assertEqual(datum.type, "int")
        self.assertEqual(datum.value, 42)

        datum = LegacyDurableClientConverter.encode(obj=3.14, expected_type=float)
        self.assertEqual(datum.type, "double")
        self.assertEqual(datum.value, 3.14)

        datum = LegacyDurableClientConverter.encode(obj=True, expected_type=bool)
        self.assertEqual(datum.type, "bool")
        self.assertTrue(datum.value)

        with self.assertRaises(NotImplementedError):
            LegacyDurableClientConverter.encode(obj=set([1, 2]), expected_type=set)

    def test_durable_client_converter_decode(self):
        data = Datum(type="string", value="abc")
        result = LegacyDurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertEqual(result, "abc")

        data = Datum(type="bytes", value=b"123")
        result = LegacyDurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertEqual(result, b"123")

        data = Datum(type="json", value={"key": "val"})
        result = LegacyDurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertEqual(result, {"key": "val"})

        data = Datum(type=None, value=None)
        result = LegacyDurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertIsNone(result)

        result = LegacyDurableClientConverter.decode(data=None, trigger_metadata=None)
        self.assertIsNone(result)

        data = Datum(type="weird", value="???")
        with self.assertRaises(ValueError):
            LegacyDurableClientConverter.decode(data=data, trigger_metadata=None)
