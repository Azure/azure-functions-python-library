# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import sys
import threading
import unittest
import warnings

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
from azure.functions import _durable_functions as df
from azure.functions.meta import Datum

CONTEXT_CLASSES = [OrchestrationContext, EntityContext]
CONVERTERS = [OrchestrationTriggerConverter, EnitityTriggerConverter]


class City:
    """Sample serializable type used by the helper tests."""

    def __init__(self, name, population):
        self.name = name
        self.population = population

    def __eq__(self, other):
        return (isinstance(other, City)
                and self.name == other.name
                and self.population == other.population)

    def to_json(self):
        return {"name": self.name, "population": self.population}

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["population"])


class PlainFromJsonClass:
    """Has from_json as an instance method (must be rejected by resolver)."""

    def to_json(self):
        return {}

    def from_json(self, data):  # not classmethod/staticmethod
        return self


class NoToJsonClass:
    """Defines from_json but no to_json (must be rejected by resolver)."""

    @classmethod
    def from_json(cls, data):
        return cls()


_NOT_A_CLASS = "i am a string"


def _from_json_function(data):
    return data


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

    def test_activity_trigger_encode_failure_exception_has_cause(self):
        class NonEncodable:
            def __init__(self):
                self.value = 'foo'

        data = NonEncodable()

        try:
            ActivityTriggerConverter.encode(data, expected_type=None)
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
            decoded = ActivityTriggerConverter.decode(
                data=datum['input'],
                trigger_metadata=None)
            self.assertEqual(decoded, datum['expected_value'])

    def test_activity_trigger_decode_failure_exception_has_cause(self):
        data = Datum('{"value": "bar"}', 'json')

        try:
            ActivityTriggerConverter.decode(
                data=data,
                trigger_metadata=None)
        except ValueError as e:
            self.assertIsNotNone(e.__cause__)
            self.assertIsInstance(e.__cause__, TypeError)

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

    def test_durable_client_converter_has_trigger_support(self):
        self.assertFalse(DurableClientConverter.has_trigger_support())

    def test_durable_client_converter_check_input_type_annotation(self):
        self.assertTrue(DurableClientConverter.check_input_type_annotation(str))
        self.assertTrue(DurableClientConverter.check_input_type_annotation(bytes))
        self.assertFalse(DurableClientConverter.check_input_type_annotation(int))

    def test_durable_client_converter_check_output_type_annotation(self):
        self.assertTrue(DurableClientConverter.check_output_type_annotation(str))
        self.assertTrue(DurableClientConverter.check_output_type_annotation(bytes))
        self.assertTrue(DurableClientConverter.check_output_type_annotation(bytearray))
        self.assertFalse(DurableClientConverter.check_output_type_annotation(int))

    def test_durable_client_converter_encode(self):
        datum = DurableClientConverter.encode(obj="hello", expected_type=str)
        self.assertEqual(datum.type, "string")
        self.assertEqual(datum.value, "hello")

        datum = DurableClientConverter.encode(obj=b"data", expected_type=bytes)
        self.assertEqual(datum.type, "bytes")
        self.assertEqual(datum.value, b"data")

        datum = DurableClientConverter.encode(obj=None, expected_type=None)
        self.assertIsNone(datum.type)
        self.assertIsNone(datum.value)

        datum = DurableClientConverter.encode(obj={"a": 1}, expected_type=dict)
        self.assertEqual(datum.type, "dict")
        self.assertEqual(datum.value, {"a": 1})

        datum = DurableClientConverter.encode(obj=[1, 2], expected_type=list)
        self.assertEqual(datum.type, "list")
        self.assertEqual(datum.value, [1, 2])

        datum = DurableClientConverter.encode(obj=42, expected_type=int)
        self.assertEqual(datum.type, "int")
        self.assertEqual(datum.value, 42)

        datum = DurableClientConverter.encode(obj=3.14, expected_type=float)
        self.assertEqual(datum.type, "double")
        self.assertEqual(datum.value, 3.14)

        datum = DurableClientConverter.encode(obj=True, expected_type=bool)
        self.assertEqual(datum.type, "bool")
        self.assertTrue(datum.value)

        with self.assertRaises(NotImplementedError):
            DurableClientConverter.encode(obj=set([1, 2]), expected_type=set)

    def test_durable_client_converter_decode(self):
        data = Datum(type="string", value="abc")
        result = DurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertEqual(result, "abc")

        data = Datum(type="bytes", value=b"123")
        result = DurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertEqual(result, b"123")

        data = Datum(type="json", value={"key": "val"})
        result = DurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertEqual(result, {"key": "val"})

        data = Datum(type=None, value=None)
        result = DurableClientConverter.decode(data=data, trigger_metadata=None)
        self.assertIsNone(result)

        result = DurableClientConverter.decode(data=None, trigger_metadata=None)
        self.assertIsNone(result)

        data = Datum(type="weird", value="???")
        with self.assertRaises(ValueError):
            DurableClientConverter.decode(data=data, trigger_metadata=None)


def _register(cls):
    """Register a class and unregister it during teardown."""
    df.register_durable_serializable_type(cls)


def _unregister_all():
    df._registered_types.clear()


class _NoLazyImports:
    """Context manager that asserts decode does not trigger lazy imports.

    Decoding is expected to be a data transformation only.
    """

    def __init__(self, testcase):
        self.tc = testcase
        self._original = None

    def __enter__(self):
        import importlib as _il
        self._original = _il.import_module

        def _fail(name, package=None):
            raise AssertionError(
                "decode triggered a lazy import: "
                f"name={name!r} package={package!r}"
            )

        _il.import_module = _fail
        return self

    def __exit__(self, *exc):
        import importlib as _il
        if self._original is not None:
            _il.import_module = self._original


class TestDurableSerializationRegistry(unittest.TestCase):

    def tearDown(self):
        _unregister_all()

    def test_register_requires_to_json_and_from_json(self):
        class Bad:
            pass

        with self.assertRaises(TypeError):
            df.register_durable_serializable_type(Bad)

    def test_register_is_idempotent_for_same_class(self):
        df.register_durable_serializable_type(City)
        df.register_durable_serializable_type(City)  # no error

    def test_register_rejects_conflicting_class(self):
        df.register_durable_serializable_type(City)

        Other = type("City", (), {
            "__module__": City.__module__,
            "__qualname__": City.__qualname__,
            "to_json": lambda self: {},
            "from_json": classmethod(lambda cls, d: cls()),
        })
        with self.assertRaises(ValueError):
            df.register_durable_serializable_type(Other)


class TestSymmetricRoundTrip(unittest.TestCase):

    def tearDown(self):
        _unregister_all()

    def _round_trip(self, value):
        return df.from_json_string(df.to_json_string(value))

    def test_plain_json_values_round_trip_unchanged(self):
        corpus = [
            None,
            True,
            False,
            0,
            -1,
            3.14,
            "",
            "hello",
            [],
            [1, 2, 3],
            {},
            {"a": 1, "b": [1, 2], "c": {"d": "e"}},
        ]
        for value in corpus:
            with self.subTest(value=value):
                self.assertEqual(self._round_trip(value), value)

    def test_dicts_with_individual_legacy_keys_round_trip_unchanged(self):
        corpus = [
            {"__class__": "X"},
            {"__module__": "M"},
            {"__data__": 1},
            {"__class__": "X", "__module__": "M"},
            {"__class__": "X", "__data__": 1},
            {"__module__": "M", "__data__": 1},
        ]
        for value in corpus:
            with self.subTest(value=value):
                self.assertEqual(self._round_trip(value), value)

    def test_dict_with_all_legacy_keys_round_trips_as_dict(self):
        forged = {"__class__": "City", "__module__": "antigravity",
                  "__data__": {}}
        self.assertEqual(self._round_trip(forged), forged)
        self.assertNotIsInstance(self._round_trip(forged), City)

    def test_nested_collisions_are_escaped_and_restored(self):
        value = {
            "outer": [
                {"__class__": "X", "__module__": "Y", "__data__": 1},
                {"__azfunc_obj__": {"t": "x", "d": 0}},
                {"__azfunc_escaped__": "x"},
                {"normal": "dict"},
            ],
        }
        self.assertEqual(self._round_trip(value), value)

    def test_registered_instance_round_trips(self):
        df.register_durable_serializable_type(City)
        c = City("Seattle", 750000)
        self.assertEqual(self._round_trip(c), c)

    def test_registered_instance_nested_in_collection(self):
        df.register_durable_serializable_type(City)
        value = {"cities": [City("A", 1), City("B", 2)], "count": 2}
        self.assertEqual(self._round_trip(value), value)

    def test_unregistered_to_json_class_raises_on_serialize(self):
        c = City("Seattle", 1)
        with self.assertRaises(TypeError):
            df.to_json_string(c)

    def test_non_json_serializable_object_raises(self):
        with self.assertRaises(TypeError):
            df.to_json_string(object())


class TestDecodeIsPureTransformation(unittest.TestCase):
    """Decode is a data operation only."""

    def tearDown(self):
        _unregister_all()

    def test_new_pipeline_with_registered_class(self):
        df.register_durable_serializable_type(City)
        s = df.to_json_string(City("X", 1))
        with _NoLazyImports(self):
            self.assertEqual(df.from_json_string(s), City("X", 1))

    def test_new_pipeline_with_unknown_marker(self):
        s = json.dumps({"__azfunc_obj__": {"t": "no.such.Thing", "d": {}}})
        with _NoLazyImports(self):
            result = df.from_json_string(s)
        self.assertEqual(
            result, {"__azfunc_obj__": {"t": "no.such.Thing", "d": {}}}
        )

    def test_legacy_string_decode_with_unloaded_module(self):
        s = json.dumps({"__class__": "Thing", "__module__": "no_such_module_xyz",
                        "__data__": {}})
        with _NoLazyImports(self), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = df.from_json_string(s, accept_legacy=True)
        self.assertEqual(result["__class__"], "Thing")

    def test_legacy_object_hook_with_loaded_module(self):
        df.register_durable_serializable_type(City)
        payload = {"__class__": "City", "__module__": City.__module__,
                   "__data__": {"name": "X", "population": 1}}
        s = json.dumps(payload)
        with _NoLazyImports(self), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            decoded = json.loads(s, object_hook=df._deserialize_custom_object)
        self.assertEqual(decoded, City("X", 1))

    def test_legacy_object_hook_with_unloaded_module(self):
        payload = {"__class__": "Thing", "__module__": "no_such_module_xyz",
                   "__data__": {}}
        with _NoLazyImports(self), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = df._deserialize_custom_object(dict(payload))
        self.assertEqual(result, payload)


class TestLegacyDecodePathFallback(unittest.TestCase):

    def tearDown(self):
        _unregister_all()
        # Restore default; individual tests may toggle.
        df._STRICT_LEGACY = False

    def test_resolver_finds_class_in_loaded_module(self):
        # City is defined in this test module (already in sys.modules).
        cls = df._resolve_loaded_class(City.__module__, "City")
        self.assertIs(cls, City)

    def test_resolver_returns_none_for_unloaded_module(self):
        self.assertNotIn("no_such_module_xyz", sys.modules)
        self.assertIsNone(
            df._resolve_loaded_class("no_such_module_xyz", "Thing")
        )

    def test_resolver_rejects_instance_method_from_json(self):
        self.assertIsNone(
            df._resolve_loaded_class(__name__, "PlainFromJsonClass")
        )

    def test_resolver_rejects_class_without_to_json(self):
        self.assertIsNone(
            df._resolve_loaded_class(__name__, "NoToJsonClass")
        )

    def test_resolver_rejects_non_class_attribute(self):
        self.assertIsNone(df._resolve_loaded_class(__name__, "_NOT_A_CLASS"))
        self.assertIsNone(
            df._resolve_loaded_class(__name__, "_from_json_function")
        )

    def test_resolver_rejects_re_export(self):
        # City re-exposed under a different module name -> rejected
        # because cls.__module__ does not match.
        fake_mod_name = "tests.test_durable_functions_fake_export"
        fake = type(sys)("fake")
        fake.City = City
        sys.modules[fake_mod_name] = fake
        try:
            self.assertIsNone(
                df._resolve_loaded_class(fake_mod_name, "City")
            )
        finally:
            sys.modules.pop(fake_mod_name, None)

    def test_legacy_decode_via_sys_modules_fallback(self):
        payload = {"__class__": "City", "__module__": City.__module__,
                   "__data__": {"name": "Y", "population": 2}}
        s = json.dumps(payload)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = df.from_json_string(s, accept_legacy=True)
        self.assertEqual(result, City("Y", 2))
        self.assertTrue(any(issubclass(w.category, DeprecationWarning)
                            for w in caught))

    def test_legacy_decode_strict_mode_returns_dict(self):
        df._STRICT_LEGACY = True
        payload = {"__class__": "City", "__module__": City.__module__,
                   "__data__": {"name": "Y", "population": 2}}
        s = json.dumps(payload)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = df.from_json_string(s, accept_legacy=True)
        self.assertEqual(result, payload)
        self.assertTrue(any(issubclass(w.category, DeprecationWarning)
                            for w in caught))

    def test_legacy_decode_unloaded_module_returns_dict(self):
        payload = {"__class__": "Thing", "__module__": "no_such_module_xyz",
                   "__data__": {}}
        s = json.dumps(payload)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = df.from_json_string(s, accept_legacy=True)
        self.assertEqual(result, payload)
        self.assertTrue(any(issubclass(w.category, DeprecationWarning)
                            for w in caught))

    def test_legacy_decode_registered_class_takes_precedence(self):
        df.register_durable_serializable_type(City)
        payload = {"__class__": "City", "__module__": City.__module__,
                   "__data__": {"name": "Z", "population": 3}}
        s = json.dumps(payload)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = df.from_json_string(s, accept_legacy=True)
        self.assertEqual(result, City("Z", 3))

    def test_legacy_decode_without_accept_legacy_returns_dict(self):
        payload = {"__class__": "City", "__module__": City.__module__,
                   "__data__": {"name": "Q", "population": 4}}
        s = json.dumps(payload)
        result = df.from_json_string(s, accept_legacy=False)
        self.assertEqual(result, payload)

    def test_legacy_decode_unregistered_returns_dict(self):
        payload = {"__class__": "Nope", "__module__": "no_such_module_xyz",
                   "__data__": {}}
        s = json.dumps(payload)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = df.from_json_string(s, accept_legacy=True)
        self.assertEqual(result, payload)


class TestLegacyShimSerialize(unittest.TestCase):

    def tearDown(self):
        _unregister_all()

    def test_serialize_unregistered_class_raises(self):
        c = City("X", 1)
        with self.assertRaises(TypeError):
            df._serialize_custom_object(c)

    def test_serialize_registered_class_emits_legacy_shape(self):
        df.register_durable_serializable_type(City)
        out = df._serialize_custom_object(City("X", 1))
        self.assertEqual(set(out.keys()),
                         {"__class__", "__module__", "__data__"})
        self.assertEqual(out["__class__"], "City")
        self.assertEqual(out["__module__"], City.__module__)
        self.assertEqual(out["__data__"], {"name": "X", "population": 1})

    def test_legacy_shim_round_trip_via_json(self):
        df.register_durable_serializable_type(City)
        s = json.dumps(City("R", 5), default=df._serialize_custom_object)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            decoded = json.loads(s, object_hook=df._deserialize_custom_object)
        self.assertEqual(decoded, City("R", 5))


class TestRegistryConcurrency(unittest.TestCase):

    def tearDown(self):
        _unregister_all()

    def test_concurrent_registration_is_safe(self):
        errors = []

        def worker():
            try:
                for _ in range(50):
                    df.register_durable_serializable_type(City)
            except Exception as exc:  # pragma: no cover - reported via errors
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])
        key = f"{City.__module__}.{City.__qualname__}"
        self.assertIs(df._registered_types[key], City)


class TestModuleSurface(unittest.TestCase):
    """Module-level imports stay minimal."""

    def test_module_does_not_expose_import_module(self):
        self.assertFalse(hasattr(df, "import_module"))
