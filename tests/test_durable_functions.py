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
        for dt in (str, bytes):
            self.assertTrue(
                OrchestrationTriggerConverter.check_input_type_annotation(dt)
            )

    def test_orchestration_trigger_check_bad_annotation(self):
        for dt in (int, OrchestrationContext):
            self.assertFalse(
                OrchestrationTriggerConverter.check_input_type_annotation(dt)
            )

    def test_orchestration_trigger_has_implicit_return(self):
        self.assertTrue(
            OrchestrationTriggerConverter.has_implicit_output()
        )

    def test_activity_trigger_accepts_any_types(self):
        datum_set = {
            Datum('string', str),
            Datum(123, int),
            Datum(1234.56, float),
            Datum('string'.encode('utf-8'), bytes),
            Datum(Datum('{ "json": true }', str), Datum)
        }

        for datum in datum_set:
            out = ActivityTriggerConverter.decode(datum, trigger_metadata=None)
            self.assertEqual(out, datum.value)
            self.assertEqual(type(out), datum.type)

    def test_activity_trigger_has_implicit_return(self):
        self.assertTrue(
            ActivityTriggerConverter.has_implicit_output()
        )
