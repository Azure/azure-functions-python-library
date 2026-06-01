# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import typing
import unittest
import warnings
from unittest import mock

from azure.functions import _durable_functions
from azure.functions._durable_functions import (
    df_dumps,
    df_loads,
    _deserialize_custom_object,
    _serialize_custom_object,
    _get_serialize_default,
)
from azure.functions.durable_functions import ActivityTriggerConverter
from azure.functions.meta import Datum


def _reset_notice_flags():
    _durable_functions._loose_codec_notice_emitted = False
    _durable_functions._no_expected_type_notice_emitted = False


class _NoticeIsolatedTestCase(unittest.TestCase):
    """Reset the one-shot notice flags before each test."""

    def setUp(self):
        _reset_notice_flags()
        self.addCleanup(_reset_notice_flags)


# ---------------------------------------------------------------------------
# Test fixtures: simple custom classes with to_json / from_json
# ---------------------------------------------------------------------------


class Hat:
    def __init__(self, color):
        self.color = color

    def __eq__(self, other):
        return isinstance(other, Hat) and self.color == other.color

    @staticmethod
    def to_json(obj):
        return {"color": obj.color}

    @staticmethod
    def from_json(data):
        return Hat(color=data["color"])


class Order:
    def __init__(self, item, hat):
        self.item = item
        self.hat = hat

    def __eq__(self, other):
        return (isinstance(other, Order)
                and self.item == other.item
                and self.hat == other.hat)

    @staticmethod
    def to_json(obj):
        # Strict-mode contract: explicitly serialize nested custom objects.
        return {"item": obj.item, "hat": Hat.to_json(obj.hat)}

    @staticmethod
    def from_json(data):
        hat_data = data["hat"]
        if isinstance(hat_data, Hat):
            hat = hat_data
        else:
            hat = Hat.from_json(hat_data)
        return Order(item=data["item"], hat=hat)


class NoFromJson:
    @staticmethod
    def to_json(obj):
        return {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strict_env(value):
    return mock.patch.dict(
        "os.environ",
        {"AZURE_FUNCTIONS_DURABLE_STRICT_TYPING": value},
    )


def _no_strict_env():
    # Ensure the env var is unset for loose-mode tests.
    env = dict()
    return mock.patch.dict("os.environ", env, clear=False)


# ---------------------------------------------------------------------------
# df_dumps
# ---------------------------------------------------------------------------


class TestDfDumps(_NoticeIsolatedTestCase):

    def test_loose_primitive_roundtrip(self):
        for value in [None, True, 1, 1.5, "x", [1, 2], {"a": 1}]:
            self.assertEqual(json.loads(df_dumps(value)), value)

    def test_loose_custom_object(self):
        s = df_dumps(Hat("red"))
        raw = json.loads(s)
        self.assertEqual(raw["__class__"], "Hat")
        self.assertEqual(raw["__module__"], Hat.__module__)
        self.assertEqual(raw["__data__"], {"color": "red"})

    def test_loose_nested_custom_via_default(self):
        # Loose mode: nested custom objects are auto-wrapped via default=.
        nested = {"hats": [Hat("red"), Hat("blue")]}
        s = df_dumps(nested)
        raw = json.loads(s)
        self.assertEqual(raw["hats"][0]["__class__"], "Hat")
        self.assertEqual(raw["hats"][1]["__data__"], {"color": "blue"})

    def test_strict_top_level_custom_object(self):
        with _strict_env("1"):
            s = df_dumps(Order(item="x", hat=Hat("red")))
        raw = json.loads(s)
        self.assertEqual(raw["__class__"], "Order")
        # __data__ must be plain JSON (no nested envelope) in strict mode.
        self.assertEqual(raw["__data__"], {"item": "x", "hat": {"color": "red"}})

    def test_strict_primitive(self):
        with _strict_env("yes"):
            self.assertEqual(df_dumps([1, 2, 3]), "[1, 2, 3]")

    def test_strict_rejects_unencodable_nested(self):
        # Strict mode does not pass default=, so a stray custom object inside
        # a plain container raises TypeError immediately.
        with _strict_env("true"):
            with self.assertRaises(TypeError):
                df_dumps({"hat": Hat("red")})


# ---------------------------------------------------------------------------
# df_loads (no expected_type)
# ---------------------------------------------------------------------------


class TestDfLoadsNoType(_NoticeIsolatedTestCase):

    def test_loose_primitive(self):
        s = json.dumps({"a": 1, "b": [2, 3]})
        self.assertEqual(df_loads(s), {"a": 1, "b": [2, 3]})

    def test_loose_custom_object_module_loaded(self):
        # Hat's module is the test module itself, which is loaded.
        s = df_dumps(Hat("red"))
        result = df_loads(s)
        self.assertEqual(result, Hat("red"))

    def test_loose_does_not_call_import_module(self):
        s = df_dumps(Hat("red"))
        with mock.patch("importlib.import_module") as imp:
            df_loads(s)
        imp.assert_not_called()

    def test_loose_unloaded_module_raises_value_error(self):
        payload = json.dumps({
            "__class__": "Whatever",
            "__module__": "definitely.not.loaded.module.xyz",
            "__data__": {},
        })
        with self.assertRaises(ValueError):
            df_loads(payload)

    def test_loose_unknown_class_in_loaded_module_raises_attribute_error(self):
        payload = json.dumps({
            "__class__": "ThisClassDoesNotExist",
            "__module__": __name__,
            "__data__": {},
        })
        with self.assertRaises(AttributeError):
            df_loads(payload)

    def test_loose_class_without_from_json_raises_type_error(self):
        payload = json.dumps({
            "__class__": "NoFromJson",
            "__module__": __name__,
            "__data__": {},
        })
        with self.assertRaises(TypeError):
            df_loads(payload)

    def test_strict_primitive_no_type(self):
        with _strict_env("1"):
            self.assertEqual(df_loads('{"a": 1}'), {"a": 1})

    def test_strict_custom_payload_no_type_raises(self):
        s = df_dumps(Hat("red"))
        with _strict_env("1"):
            with self.assertRaises(TypeError):
                df_loads(s)


# ---------------------------------------------------------------------------
# df_loads (with expected_type)
# ---------------------------------------------------------------------------


class TestDfLoadsWithType(_NoticeIsolatedTestCase):

    def test_loose_match_uses_object_hook(self):
        # Loose mode preserves the legacy object_hook path so nested custom
        # objects inside __data__ are also reconstructed.  importlib is
        # still never called because _deserialize_custom_object now uses
        # sys.modules.
        s = df_dumps(Hat("red"))
        with mock.patch("importlib.import_module") as imp:
            result = df_loads(s, expected_type=Hat)
        imp.assert_not_called()
        self.assertEqual(result, Hat("red"))

    def test_loose_mismatch_warns_and_falls_through(self):
        # Encode a Hat but ask for an Order -- mismatch in loose mode logs
        # a warning, then falls through to object_hook, which reconstructs
        # Hat (its module is loaded).
        s = df_dumps(Hat("red"))
        with self.assertLogs("azure.functions.DurableFunctions",
                             level="WARNING") as cm:
            result = df_loads(s, expected_type=Order)
        self.assertTrue(any("payload declares" in m for m in cm.output))
        self.assertEqual(result, Hat("red"))

    def test_strict_match_uses_from_json_directly(self):
        with _strict_env("1"):
            s = df_dumps(Order(item="x", hat=Hat("red")))
            with mock.patch("importlib.import_module") as imp:
                result = df_loads(s, expected_type=Order)
        imp.assert_not_called()
        self.assertEqual(result, Order(item="x", hat=Hat("red")))

    def test_strict_mismatch_raises(self):
        s = df_dumps(Hat("red"))
        with _strict_env("1"):
            with self.assertRaises(TypeError):
                df_loads(s, expected_type=Order)

    def test_strict_type_without_from_json_raises(self):
        # Build an envelope that names NoFromJson; with the matching
        # expected_type strict mode should reject it.
        payload = json.dumps({
            "__class__": "NoFromJson",
            "__module__": __name__,
            "__data__": {},
        })
        with _strict_env("1"):
            with self.assertRaises(TypeError):
                df_loads(payload, expected_type=NoFromJson)

    def test_primitive_type_validation_loose_mismatch_warns(self):
        s = json.dumps("hello")
        with self.assertLogs("azure.functions.DurableFunctions",
                             level="WARNING") as cm:
            result = df_loads(s, expected_type=int)
        self.assertTrue(any("not compatible" in m for m in cm.output))
        self.assertEqual(result, "hello")

    def test_primitive_type_validation_strict_mismatch_raises(self):
        s = json.dumps("hello")
        with _strict_env("1"):
            with self.assertRaises(TypeError):
                df_loads(s, expected_type=int)

    def test_typing_generics_do_not_crash(self):
        # isinstance(value, List[int]) raises TypeError; df_loads tolerates it.
        s = json.dumps([1, 2, 3])
        result = df_loads(s, expected_type=typing.List[int])
        self.assertEqual(result, [1, 2, 3])


# ---------------------------------------------------------------------------
# _get_serialize_default
# ---------------------------------------------------------------------------


class TestGetSerializeDefault(_NoticeIsolatedTestCase):

    def test_loose_returns_serializer(self):
        self.assertIs(_get_serialize_default(), _serialize_custom_object)

    def test_strict_returns_none(self):
        with _strict_env("1"):
            self.assertIsNone(_get_serialize_default())


# ---------------------------------------------------------------------------
# _deserialize_custom_object direct
# ---------------------------------------------------------------------------


class TestDeserializeCustomObjectDirect(_NoticeIsolatedTestCase):

    def test_module_loaded_reconstructs(self):
        result = _deserialize_custom_object({
            "__class__": "Hat",
            "__module__": __name__,
            "__data__": {"color": "red"},
        })
        self.assertEqual(result, Hat("red"))

    def test_module_not_loaded_raises_value_error(self):
        with self.assertRaises(ValueError):
            _deserialize_custom_object({
                "__class__": "Whatever",
                "__module__": "definitely.not.loaded.xyz",
                "__data__": {},
            })

    def test_does_not_import_module(self):
        # Ensure the symbol isn't even referenced.
        with mock.patch("importlib.import_module") as imp:
            _deserialize_custom_object({
                "__class__": "Hat",
                "__module__": __name__,
                "__data__": {"color": "blue"},
            })
        imp.assert_not_called()

    def test_non_envelope_passthrough(self):
        d = {"a": 1}
        self.assertEqual(_deserialize_custom_object(d), {"a": 1})


# ---------------------------------------------------------------------------
# ActivityTriggerConverter integration
# ---------------------------------------------------------------------------


class TestActivityTriggerConverterIntegration(_NoticeIsolatedTestCase):

    def test_decode_uses_df_loads(self):
        datum = Datum(type="json", value=json.dumps({"x": 1}))
        with mock.patch.object(_durable_functions, "df_loads",
                               wraps=_durable_functions.df_loads) as spy:
            ActivityTriggerConverter.decode(datum, trigger_metadata=None)
        spy.assert_called_once_with(datum.value)

    def test_encode_uses_df_dumps(self):
        with mock.patch.object(_durable_functions, "df_dumps",
                               wraps=_durable_functions.df_dumps) as spy:
            ActivityTriggerConverter.encode({"x": 1}, expected_type=None)
        spy.assert_called_once_with({"x": 1})

    def test_decode_custom_object_loaded_module(self):
        s = df_dumps(Hat("green"))
        datum = Datum(type="json", value=s)
        result = ActivityTriggerConverter.decode(datum, trigger_metadata=None)
        self.assertEqual(result, Hat("green"))

    def test_decode_unloaded_module_raises_value_error(self):
        payload = json.dumps({
            "__class__": "Whatever",
            "__module__": "definitely.not.loaded.xyz",
            "__data__": {},
        })
        datum = Datum(type="json", value=payload)
        with self.assertRaises(ValueError):
            ActivityTriggerConverter.decode(datum, trigger_metadata=None)

    def test_encode_unserializable_raises_value_error(self):
        class NotSerializable:
            pass
        with self.assertRaises(ValueError):
            ActivityTriggerConverter.encode(NotSerializable(),
                                            expected_type=None)


# ---------------------------------------------------------------------------
# One-shot loose-mode notices
# ---------------------------------------------------------------------------


class TestLooseModeNotices(_NoticeIsolatedTestCase):

    def test_loose_codec_notice_fires_once(self):
        s = df_dumps(Hat("red"))
        with self.assertLogs("azure.functions.DurableFunctions",
                             level="INFO") as cm, \
                warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            df_loads(s)
            df_loads(s)  # second call must not emit again
            df_loads(s)
        self.assertEqual(
            sum("loose-mode object_hook" in m for m in cm.output), 1)
        self.assertEqual(
            sum(issubclass(w.category, DeprecationWarning)
                and "loose-mode object_hook" in str(w.message)
                for w in caught),
            1,
        )

    def test_loose_codec_notice_not_emitted_for_primitive(self):
        # No custom-object reconstruction -> no loose-codec notice.
        with self.assertNoLogs(_durable_functions.__name__, level="INFO"):
            df_loads(json.dumps({"a": 1}), expected_type=dict)
        self.assertFalse(
            _durable_functions._loose_codec_notice_emitted)

    def test_loose_codec_notice_suppressed_in_strict_mode(self):
        s = df_dumps(Hat("red"))
        with _strict_env("1"):
            # In strict mode df_loads with expected_type uses from_json
            # directly -- the object_hook path doesn't fire.  Even if it
            # did, the notice helper short-circuits in strict mode.
            df_loads(s, expected_type=Hat)
        self.assertFalse(
            _durable_functions._loose_codec_notice_emitted)

    def test_no_expected_type_notice_fires_once(self):
        s = json.dumps({"a": 1})
        with self.assertLogs("azure.functions.DurableFunctions",
                             level="INFO") as cm, \
                warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            df_loads(s)
            df_loads(s)
            df_loads(s)
        self.assertEqual(
            sum("without expected_type" in m for m in cm.output), 1)
        self.assertEqual(
            sum(issubclass(w.category, DeprecationWarning)
                and "without expected_type" in str(w.message)
                for w in caught),
            1,
        )

    def test_no_expected_type_notice_not_emitted_when_type_provided(self):
        s = json.dumps({"a": 1})
        with self.assertNoLogs(_durable_functions.__name__, level="INFO"):
            df_loads(s, expected_type=dict)
        self.assertFalse(
            _durable_functions._no_expected_type_notice_emitted)

    def test_no_expected_type_notice_suppressed_in_strict_mode(self):
        s = json.dumps({"a": 1})
        with _strict_env("1"):
            df_loads(s)
        self.assertFalse(
            _durable_functions._no_expected_type_notice_emitted)


if __name__ == "__main__":
    unittest.main()
