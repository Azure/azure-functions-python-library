# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import unittest
import json
from unittest import mock

from azure.functions.durable_functions import (
    LegacyOrchestrationTriggerConverter,
    LegacyEnitityTriggerConverter,
    LegacyActivityTriggerConverter,
    LegacyDurableClientConverter,
    OrchestrationTriggerConverter,
    EnitityTriggerConverter,
    ActivityTriggerConverter,
    DurableClientConverter,
    register_durable_converters,
)
from azure.functions.decorators import durable_functions as df_decorators
from azure.functions._durable_functions import (
    OrchestrationContext,
    EntityContext
)
from azure.functions import meta
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


V2_CONTEXT_CLASSES = [OrchestrationContext, EntityContext]
V2_TRIGGER_CONVERTERS = [OrchestrationTriggerConverter, EnitityTriggerConverter]


class TestDurableFunctionsV2Converters(unittest.TestCase):
    """Tests for the Durable Task (v2.x) Durable Functions converters."""

    def test_trigger_converter_decode(self):
        datum = Datum(value='{ "name": "great function" }', type=str)
        for converter in V2_TRIGGER_CONVERTERS:
            ctx = converter.decode(datum, trigger_metadata=None)
            content = json.loads(ctx.body)
            self.assertEqual(content.get('name'), 'great function')

    def test_trigger_converter_encode_uses_string(self):
        # The v2 converters encode the context as a string, unlike the
        # legacy converters which encode as json.
        for converter in V2_TRIGGER_CONVERTERS:
            datum = converter.encode('some-context', expected_type=None)
            self.assertEqual(datum.type, 'string')
            self.assertEqual(datum.value, 'some-context')

    def test_trigger_check_good_annotation(self):
        for converter, ctx in zip(V2_TRIGGER_CONVERTERS, V2_CONTEXT_CLASSES):
            self.assertTrue(converter.check_input_type_annotation(ctx))

    def test_trigger_check_bad_annotation(self):
        for dt in (str, bytes, int):
            for converter in V2_TRIGGER_CONVERTERS:
                self.assertFalse(converter.check_input_type_annotation(dt))

    def test_trigger_check_output_type_annotation(self):
        for converter in V2_TRIGGER_CONVERTERS:
            self.assertTrue(converter.check_output_type_annotation(pytype=None))

    def test_trigger_has_implicit_return(self):
        for converter in V2_TRIGGER_CONVERTERS:
            self.assertTrue(converter.has_implicit_output())

    def test_activity_trigger_decode(self):
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

    def test_activity_trigger_decode_string_failover(self):
        # Non-json serializable strings fail over to the raw string value.
        datum = Datum('sample_string', 'string')
        decoded = ActivityTriggerConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertEqual(decoded, 'sample_string')

    def test_activity_trigger_encode(self):
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
                'output': list(["do", "re", "mi"]),
                'expected_value': Datum('["do", "re", "mi"]', 'json')
            },
        ]

        for datum in data:
            encoded = ActivityTriggerConverter.encode(
                obj=datum['output'],
                expected_type=type(datum['output']))
            self.assertEqual(encoded, datum['expected_value'])

    def test_activity_trigger_encode_failure_exception_has_cause(self):
        class NonEncodable:
            def __init__(self):
                self.value = 'foo'

        try:
            ActivityTriggerConverter.encode(NonEncodable(), expected_type=None)
        except ValueError as e:
            self.assertIsNotNone(e.__cause__)
            self.assertIsInstance(e.__cause__, TypeError)

    def test_activity_trigger_decode_no_implementation_exception(self):
        datum = Datum(value=b"dummy", type="bytes")
        with self.assertRaises(NotImplementedError):
            ActivityTriggerConverter.decode(data=datum, trigger_metadata=None)

    def test_activity_trigger_has_implicit_return(self):
        self.assertTrue(ActivityTriggerConverter.has_implicit_output())

    def test_durable_client_no_implicit_return(self):
        self.assertFalse(DurableClientConverter.has_implicit_output())

    def test_durable_client_converter_has_trigger_support(self):
        self.assertFalse(DurableClientConverter.has_trigger_support())

    def test_durable_client_converter_check_output_type_annotation(self):
        self.assertTrue(
            DurableClientConverter.check_output_type_annotation(str))
        self.assertTrue(
            DurableClientConverter.check_output_type_annotation(bytes))
        self.assertTrue(
            DurableClientConverter.check_output_type_annotation(bytearray))
        self.assertFalse(
            DurableClientConverter.check_output_type_annotation(int))

    def test_durable_client_converter_encode(self):
        datum = DurableClientConverter.encode(obj="hello", expected_type=str)
        self.assertEqual(datum.type, "string")
        self.assertEqual(datum.value, "hello")

        datum = DurableClientConverter.encode(obj=b"data", expected_type=bytes)
        self.assertEqual(datum.type, "bytes")
        self.assertEqual(datum.value, b"data")

        datum = DurableClientConverter.encode(obj=None, expected_type=None)
        self.assertIsNone(datum.type)

        with self.assertRaises(NotImplementedError):
            DurableClientConverter.encode(obj=set([1, 2]), expected_type=set)

    def test_durable_client_converter_check_input_type_annotation(self):
        class FakeDurableFunctionsClient:
            pass

        fake_adf = mock.MagicMock()
        fake_adf.DurableFunctionsClient = FakeDurableFunctionsClient

        with mock.patch.object(
                sys.modules['azure.functions.durable_functions'],
                'get_durable_package', return_value=fake_adf):
            self.assertTrue(
                DurableClientConverter.check_input_type_annotation(str))
            self.assertTrue(
                DurableClientConverter.check_input_type_annotation(bytes))
            self.assertTrue(
                DurableClientConverter.check_input_type_annotation(
                    FakeDurableFunctionsClient))
            self.assertFalse(
                DurableClientConverter.check_input_type_annotation(int))

    def test_durable_client_converter_decode(self):
        class FakeDurableFunctionsClient:
            def __init__(self, value):
                self.value = value

        fake_adf = mock.MagicMock()
        fake_adf.DurableFunctionsClient = FakeDurableFunctionsClient

        with mock.patch.object(
                sys.modules['azure.functions.durable_functions'],
                'get_durable_package', return_value=fake_adf):
            data = Datum(type="string", value="instance-id")
            result = DurableClientConverter.decode(
                data=data, trigger_metadata=None)
            self.assertIsInstance(result, FakeDurableFunctionsClient)
            self.assertEqual(result.value, "instance-id")


class TestRegisterDurableConverters(unittest.TestCase):
    """Tests for register_durable_converters and get_durable_package."""

    def setUp(self):
        # Preserve and restore the global binding registry so tests do not
        # leak state between one another.
        self._original_bindings = dict(meta._ConverterMeta._bindings)
        # Reset the cached durable package before each test.
        df_decorators.df = None

    def tearDown(self):
        meta._ConverterMeta._bindings.clear()
        meta._ConverterMeta._bindings.update(self._original_bindings)
        df_decorators.df = None

    def test_register_noop_when_package_missing(self):
        before = dict(meta._ConverterMeta._bindings)
        with mock.patch.object(
                sys.modules['azure.functions.durable_functions'],
                'get_durable_package', return_value=None):
            register_durable_converters()

        self.assertEqual(meta._ConverterMeta._bindings, before)

    def test_register_legacy_converters(self):
        legacy_pkg = mock.MagicMock(spec=['__name__'])
        legacy_pkg.__name__ = 'azure.durable_functions'

        with mock.patch.object(
                sys.modules['azure.functions.durable_functions'],
                'get_durable_package', return_value=legacy_pkg):
            register_durable_converters()

        bindings = meta._ConverterMeta._bindings
        self.assertIs(
            bindings["orchestrationTrigger"],
            LegacyOrchestrationTriggerConverter)
        self.assertIs(
            bindings["entityTrigger"], LegacyEnitityTriggerConverter)
        self.assertIs(
            bindings["activityTrigger"], LegacyActivityTriggerConverter)
        self.assertIs(
            bindings["durableClient"], LegacyDurableClientConverter)

    def test_register_v2_converters(self):
        v2_pkg = mock.MagicMock(spec=['__name__', 'version'])
        v2_pkg.__name__ = 'azure.durable_functions'
        v2_pkg.version = '2.0.0'

        with mock.patch.object(
                sys.modules['azure.functions.durable_functions'],
                'get_durable_package', return_value=v2_pkg):
            register_durable_converters()

        bindings = meta._ConverterMeta._bindings
        self.assertIs(
            bindings["orchestrationTrigger"], OrchestrationTriggerConverter)
        self.assertIs(bindings["entityTrigger"], EnitityTriggerConverter)
        self.assertIs(bindings["activityTrigger"], ActivityTriggerConverter)
        self.assertIs(bindings["durableClient"], DurableClientConverter)

    def test_get_durable_package_not_installed(self):
        with mock.patch.dict(sys.modules, {'azure.durable_functions': None}):
            df_decorators.df = None
            self.assertIsNone(df_decorators.get_durable_package())

    def test_get_durable_package_v2_detection(self):
        import azure.durable_functions as adf
        df_decorators.df = None
        with mock.patch.object(adf, 'version', '2.5.0', create=True):
            self.assertIs(df_decorators.get_durable_package(), adf)

    def test_get_durable_package_caches_result(self):
        import azure.durable_functions as adf
        df_decorators.df = None
        first = df_decorators.get_durable_package()
        self.assertIs(first, adf)
        # A subsequent call returns the cached reference.
        self.assertIs(df_decorators.get_durable_package(), first)
