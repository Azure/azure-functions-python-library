import unittest
import json

from azure.functions.durable_functions import (
    OrchestrationTriggerConverter,
    ActivityTriggerConverter
)
from azure.functions._durable_functions import OrchestrationContext
from azure.functions.meta import Datum


class TestDurableFunctions(unittest.TestCase):
    def test_orchestration_context_string_body(self):
        raw_string = '{ "name": "great function" }'
        context = OrchestrationContext(raw_string)
        self.assertIsNotNone(getattr(context, 'body', None))

        content = json.loads(context.body)
        self.assertEqual(content.get('name'), 'great function')

    def test_orchestration_context_string_cast(self):
        raw_string = '{ "name": "great function" }'
        context = OrchestrationContext(raw_string)
        self.assertEqual(str(context), raw_string)

        content = json.loads(str(context))
        self.assertEqual(content.get('name'), 'great function')

    def test_orchestration_context_bytes_body(self):
        raw_bytes = '{ "name": "great function" }'.encode('utf-8')
        context = OrchestrationContext(raw_bytes)
        self.assertIsNotNone(getattr(context, 'body', None))

        content = json.loads(context.body)
        self.assertEqual(content.get('name'), 'great function')

    def test_orchestration_context_bytes_cast(self):
        raw_bytes = '{ "name": "great function" }'.encode('utf-8')
        context = OrchestrationContext(raw_bytes)
        self.assertIsNotNone(getattr(context, 'body', None))

        content = json.loads(context.body)
        self.assertEqual(content.get('name'), 'great function')

    def test_orchestration_trigger_converter(self):
        datum = Datum(value='{ "name": "great function" }',
                      type=str)
        otc = OrchestrationTriggerConverter.decode(datum,
                                                   trigger_metadata=None)
        content = json.loads(otc.body)
        self.assertEqual(content.get('name'), 'great function')

    def test_orchestration_trigger_converter_type(self):
        datum = Datum(value='{ "name": "great function" }'.encode('utf-8'),
                      type=bytes)
        otc = OrchestrationTriggerConverter.decode(datum,
                                                   trigger_metadata=None)
        content = json.loads(otc.body)
        self.assertEqual(content.get('name'), 'great function')

    def test_orchestration_trigger_check_good_annotation(self):
        for dt in (OrchestrationContext,):
            self.assertTrue(
                OrchestrationTriggerConverter.check_input_type_annotation(dt)
            )

    def test_orchestration_trigger_check_bad_annotation(self):
        for dt in (str, bytes, int):
            self.assertFalse(
                OrchestrationTriggerConverter.check_input_type_annotation(dt)
            )

    def test_orchestration_trigger_has_implicit_return(self):
        self.assertTrue(
            OrchestrationTriggerConverter.has_implicit_output()
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
