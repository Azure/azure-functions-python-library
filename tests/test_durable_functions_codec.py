"""Comprehensive round-trip and validation tests for the Durable Functions codec.

Every data shape is tested in three configurations:
  1. No expected_type  (legacy object_hook path)
  2. Loose mode + expected_type  (warn on mismatch, legacy deserialize)
  3. Strict mode + expected_type  (raise on mismatch, from_json directly)

Ported from azure-functions-durable-python's df_serialization test suite.
"""

import json
import logging

import pytest

from azure.functions import _durable_functions as df_serialization
from azure.functions._durable_functions import (
    _STRICT_ENV_VAR,
    _get_serialize_default,
    df_dumps,
    df_loads,
)


# ---------------------------------------------------------------------------
# Helper classes
# ---------------------------------------------------------------------------

class PlainPerson:
    """Simple class: to_json returns a dict, from_json accepts a dict."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @staticmethod
    def to_json(obj):
        return {"name": obj.name, "age": obj.age}

    @staticmethod
    def from_json(data):
        return PlainPerson(data["name"], data["age"])

    def __eq__(self, other):
        return (isinstance(other, PlainPerson)
                and self.name == other.name and self.age == other.age)


class ScalarPerson:
    """to_json returns a scalar (str), not a dict."""

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def to_json(obj):
        return obj.name

    @staticmethod
    def from_json(data):
        return ScalarPerson(data)

    def __eq__(self, other):
        return isinstance(other, ScalarPerson) and self.name == other.name


class Hat:
    """Leaf object for nesting tests."""

    def __init__(self, color: str):
        self.color = color

    @staticmethod
    def to_json(obj):
        return {"color": obj.color}

    @staticmethod
    def from_json(data):
        return Hat(data["color"])

    def __eq__(self, other):
        return isinstance(other, Hat) and self.color == other.color


class NaiveOrder:
    """Nested object whose from_json expects pre-constructed Hat instances.

    This relies on the bottom-up object_hook behavior -- from_json receives
    a Hat instance at data["hat"], not a raw dict. Works in loose mode but
    fails in strict mode because strict skips object_hook.
    """

    def __init__(self, item: str, hat: Hat):
        self.item = item
        self.hat = hat

    @staticmethod
    def to_json(obj):
        return {"item": obj.item, "hat": obj.hat}

    @staticmethod
    def from_json(data):
        # Assumes data["hat"] is already a Hat instance (object_hook fired)
        return NaiveOrder(data["item"], data["hat"])

    def __eq__(self, other):
        return (isinstance(other, NaiveOrder)
                and self.item == other.item and self.hat == other.hat)


class SmartOrder:
    """Nested object with strict-mode-compatible to_json / from_json.

    to_json produces plain JSON (calls Hat.to_json explicitly), so the
    result is natively JSON-serializable without ``default=``.  from_json
    handles both the strict-mode shape (plain dict from to_json) and
    the loose-mode shape (pre-constructed Hat or raw legacy dict).
    """

    def __init__(self, item: str, hat: Hat):
        self.item = item
        self.hat = hat

    @staticmethod
    def to_json(obj):
        return {"item": obj.item, "hat": Hat.to_json(obj.hat)}

    @staticmethod
    def from_json(data):
        hat_data = data["hat"]
        if isinstance(hat_data, Hat):
            # Loose mode: object_hook already constructed the Hat
            hat = hat_data
        else:
            # Strict mode or plain dict: reconstruct from to_json output
            hat = Hat.from_json(hat_data)
        return SmartOrder(data["item"], hat)

    def __eq__(self, other):
        return (isinstance(other, SmartOrder)
                and self.item == other.item and self.hat == other.hat)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_one_shot_notices():
    """Reset module-level one-shot notice flags around every test.

    df_serialization fires INFO + DeprecationWarning at most once per
    process for (a) loose-mode reconstruction and (b) df_loads called
    without expected_type.  Without this reset the parametrized sweeps
    below would only see the first emission.
    """
    df_serialization._loose_codec_notice_emitted = False
    df_serialization._no_expected_type_notice_emitted = False
    yield
    df_serialization._loose_codec_notice_emitted = False
    df_serialization._no_expected_type_notice_emitted = False


@pytest.fixture
def strict(monkeypatch):
    """Enable strict typing mode for the duration of a test."""
    monkeypatch.setenv(_STRICT_ENV_VAR, "1")


@pytest.fixture
def loose(monkeypatch):
    """Explicitly disable strict typing mode."""
    monkeypatch.delenv(_STRICT_ENV_VAR, raising=False)


# ===================================================================
# 1. PRIMITIVES  (str, int, float, bool, None, list, dict)
# ===================================================================

@pytest.mark.parametrize("value", [
    None,
    True,
    False,
    0,
    -1,
    42,
    3.14,
    "",
    "hello",
    [],
    [1, 2, 3],
    [True, None, "mixed"],
    {},
    {"a": 1, "b": [1, 2]},
    {"nested": {"deep": {"value": 7}}},
])
class TestPrimitiveRoundTrips:
    """Primitives must round-trip identically in all three paths."""

    def test_no_expected_type(self, value):
        assert df_loads(df_dumps(value)) == value

    def test_loose_with_matching_type(self, value, loose, caplog):
        et = type(value) if value is not None else type(None)
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            result = df_loads(df_dumps(value), expected_type=et)
        assert result == value

    def test_strict_with_matching_type(self, value, strict):
        et = type(value) if value is not None else type(None)
        result = df_loads(df_dumps(value), expected_type=et)
        assert result == value


# ===================================================================
# 2. SIMPLE CUSTOM OBJECTS  (dict-returning to_json)
# ===================================================================

class TestSimpleObject:

    def test_no_expected_type(self):
        obj = PlainPerson("andy", 99)
        decoded = df_loads(df_dumps(obj))
        assert decoded == obj

    def test_loose_matching_type(self, loose):
        obj = PlainPerson("andy", 99)
        decoded = df_loads(df_dumps(obj), expected_type=PlainPerson)
        assert decoded == obj

    def test_strict_matching_type(self, strict):
        obj = PlainPerson("andy", 99)
        decoded = df_loads(df_dumps(obj), expected_type=PlainPerson)
        assert decoded == obj

    def test_loose_mismatched_type_warns(self, loose, caplog):
        encoded = df_dumps(PlainPerson("a", 1))
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            decoded = df_loads(encoded, expected_type=ScalarPerson)
        # Loose mode: legacy decoder uses the payload's class
        assert isinstance(decoded, PlainPerson)
        assert any("payload declares class" in r.message for r in caplog.records)

    def test_strict_mismatched_type_raises(self, strict):
        encoded = df_dumps(PlainPerson("a", 1))
        with pytest.raises(TypeError, match="payload declares class"):
            df_loads(encoded, expected_type=ScalarPerson)


# ===================================================================
# 3. SCALAR-RETURNING to_json
# ===================================================================

class TestScalarToJson:

    def test_no_expected_type(self):
        obj = ScalarPerson("andy")
        decoded = df_loads(df_dumps(obj))
        assert decoded == obj

    def test_loose_matching_type(self, loose):
        obj = ScalarPerson("andy")
        decoded = df_loads(df_dumps(obj), expected_type=ScalarPerson)
        assert decoded == obj

    def test_strict_matching_type(self, strict):
        obj = ScalarPerson("andy")
        decoded = df_loads(df_dumps(obj), expected_type=ScalarPerson)
        assert decoded == obj

    def test_loose_mismatched_type_warns(self, loose, caplog):
        encoded = df_dumps(ScalarPerson("andy"))
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            decoded = df_loads(encoded, expected_type=PlainPerson)
        # Loose mode: legacy decoder still uses the payload's class.
        assert isinstance(decoded, ScalarPerson)
        assert any("payload declares class" in r.message for r in caplog.records)

    def test_strict_mismatched_type_raises(self, strict):
        encoded = df_dumps(ScalarPerson("andy"))
        with pytest.raises(TypeError, match="payload declares class"):
            df_loads(encoded, expected_type=PlainPerson)


# ===================================================================
# 4. DICT WITH OBJECT PROPERTIES  e.g. {"person": PlainPerson(...)}
# ===================================================================

class TestDictWithObjectProperty:
    """A plain dict containing a custom object as a value."""

    def _make_payload(self):
        return {"person": PlainPerson("a", 1), "count": 7}

    def test_no_expected_type(self):
        """Loose path: object_hook reconstructs nested objects."""
        decoded = df_loads(df_dumps(self._make_payload()))
        assert decoded["count"] == 7
        assert isinstance(decoded["person"], PlainPerson)
        assert decoded["person"].name == "a"

    def test_loose_expected_dict(self, loose, caplog):
        """Loose path + expected_type=dict: works, inner objects reconstructed."""
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            decoded = df_loads(df_dumps(self._make_payload()), expected_type=dict)
        assert isinstance(decoded["person"], PlainPerson)
        # No warning -- top-level is a dict matching expected_type
        assert not any("not compatible" in r.message for r in caplog.records)

    def test_strict_encode_fails_for_nested_custom_objects(self, strict):
        """Strict mode: a plain dict containing a custom object cannot be
        encoded -- json.dumps runs without default= so PlainPerson raises
        TypeError."""
        with pytest.raises(TypeError):
            df_dumps(self._make_payload())


# ===================================================================
# 5. NESTED OBJECTS -- "naive" from_json (expects pre-constructed)
# ===================================================================

class TestNaiveNestedObject:
    """NaiveOrder.from_json expects Hat to already be a Hat instance."""

    def _make(self):
        return NaiveOrder("widget", Hat("red"))

    def test_no_expected_type(self):
        """Legacy path: object_hook fires bottom-up, Hat constructed first."""
        decoded = df_loads(df_dumps(self._make()))
        assert isinstance(decoded, NaiveOrder)
        assert isinstance(decoded.hat, Hat)
        assert decoded.hat.color == "red"

    def test_loose_matching_type(self, loose):
        """Loose + expected_type: legacy path still fires, nested works."""
        decoded = df_loads(df_dumps(self._make()), expected_type=NaiveOrder)
        assert decoded == self._make()

    def test_strict_encode_fails_for_naive_to_json(self, strict):
        """Strict mode: NaiveOrder.to_json returns a Hat instance, which
        is not natively JSON-serializable. df_dumps should fail at encode."""
        with pytest.raises(TypeError):
            df_dumps(self._make())


# ===================================================================
# 6. NESTED OBJECTS -- "smart" from_json (handles raw dicts)
# ===================================================================

class TestSmartNestedObject:
    """SmartOrder.from_json manually calls Hat.from_json when needed."""

    def _make(self):
        return SmartOrder("gadget", Hat("blue"))

    def test_no_expected_type(self):
        decoded = df_loads(df_dumps(self._make()))
        assert isinstance(decoded, SmartOrder)
        assert decoded.hat == Hat("blue")

    def test_loose_matching_type(self, loose):
        decoded = df_loads(df_dumps(self._make()), expected_type=SmartOrder)
        assert decoded == self._make()

    def test_strict_matching_type(self, strict):
        """Strict mode works: SmartOrder.from_json handles the raw dict."""
        decoded = df_loads(df_dumps(self._make()), expected_type=SmartOrder)
        assert decoded == self._make()
        assert isinstance(decoded.hat, Hat)
        assert decoded.hat.color == "blue"


# ===================================================================
# 7. LIST OF OBJECTS
# ===================================================================

class TestListOfObjects:

    def _make(self):
        return [PlainPerson("a", 1), PlainPerson("b", 2)]

    def test_no_expected_type(self):
        decoded = df_loads(df_dumps(self._make()))
        assert len(decoded) == 2
        assert all(isinstance(p, PlainPerson) for p in decoded)

    def test_loose_expected_list(self, loose):
        decoded = df_loads(df_dumps(self._make()), expected_type=list)
        assert len(decoded) == 2
        assert all(isinstance(p, PlainPerson) for p in decoded)

    def test_strict_encode_fails_for_nested_custom_objects(self, strict):
        """Strict mode: a list of custom objects cannot be encoded -- the
        list itself doesn't have to_json, and json.dumps runs without
        default= so PlainPerson raises TypeError."""
        with pytest.raises(TypeError):
            df_dumps(self._make())


# ===================================================================
# 8. PRIMITIVE TYPE MISMATCHES
# ===================================================================

class TestPrimitiveTypeMismatch:

    def test_loose_warns(self, loose, caplog):
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            result = df_loads(df_dumps("hello"), expected_type=int)
        assert result == "hello"
        assert any("not compatible" in r.message for r in caplog.records)

    def test_strict_raises(self, strict):
        with pytest.raises(TypeError, match="not compatible with expected type"):
            df_loads(df_dumps("hello"), expected_type=int)

    def test_loose_str_expected_dict_warns(self, loose, caplog):
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            result = df_loads(df_dumps("hello"), expected_type=dict)
        assert result == "hello"
        assert any("not compatible" in r.message for r in caplog.records)

    def test_strict_str_expected_dict_raises(self, strict):
        with pytest.raises(TypeError):
            df_loads(df_dumps("hello"), expected_type=dict)


# ===================================================================
# 9. typing CONSTRUCTS (List[int], Optional[str], etc.)
# ===================================================================

class TestTypingConstructs:
    """Generic type hints can't be validated with isinstance -- we pass
    through without error in both modes."""

    def test_loose_list_of_int(self, loose):
        from typing import List
        decoded = df_loads(df_dumps([1, 2, 3]), expected_type=List[int])
        assert decoded == [1, 2, 3]

    def test_strict_list_of_int(self, strict):
        from typing import List
        decoded = df_loads(df_dumps([1, 2, 3]), expected_type=List[int])
        assert decoded == [1, 2, 3]

    def test_loose_optional_str(self, loose):
        from typing import Optional
        decoded = df_loads(df_dumps("hi"), expected_type=Optional[str])
        assert decoded == "hi"

    def test_strict_optional_str(self, strict):
        from typing import Optional
        decoded = df_loads(df_dumps("hi"), expected_type=Optional[str])
        assert decoded == "hi"


# ===================================================================
# 10. STRICT MODE ENV VAR VALUES
# ===================================================================

class TestStrictModeEnvVar:

    @pytest.mark.parametrize("val", ["1", "true", "yes", "TRUE", "Yes", " 1 "])
    def test_truthy_values_enable_strict(self, monkeypatch, val):
        monkeypatch.setenv(_STRICT_ENV_VAR, val)
        with pytest.raises(TypeError):
            df_loads(df_dumps("hello"), expected_type=int)

    @pytest.mark.parametrize("val", ["0", "false", "no", "", "nope"])
    def test_non_truthy_values_stay_loose(self, monkeypatch, val, caplog):
        monkeypatch.setenv(_STRICT_ENV_VAR, val)
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            result = df_loads(df_dumps("hello"), expected_type=int)
        assert result == "hello"

    def test_unset_is_loose(self, monkeypatch):
        monkeypatch.delenv(_STRICT_ENV_VAR, raising=False)
        result = df_loads(df_dumps("hello"), expected_type=int)
        assert result == "hello"


# ===================================================================
# 10b. STRICT MODE WITHOUT expected_type
# ===================================================================

class TestStrictNoExpectedType:
    """In strict mode, df_loads without expected_type must not attempt
    custom-object reconstruction."""

    def test_primitive_returns_raw(self, strict):
        assert df_loads(df_dumps(42)) == 42

    def test_string_returns_raw(self, strict):
        assert df_loads(df_dumps("hello")) == "hello"

    def test_none_returns_raw(self, strict):
        assert df_loads(df_dumps(None)) is None

    def test_plain_dict_returns_raw(self, strict):
        d = {"key": "value", "n": 1}
        assert df_loads(df_dumps(d)) == d

    def test_plain_list_returns_raw(self, strict):
        lst = [1, "two", None]
        assert df_loads(df_dumps(lst)) == lst

    def test_custom_object_raises(self, strict):
        s = df_dumps(PlainPerson("alice", 30))
        with pytest.raises(TypeError, match="strict mode requires expected_type"):
            df_loads(s)

    def test_custom_object_error_includes_class(self, strict):
        s = df_dumps(PlainPerson("alice", 30))
        with pytest.raises(TypeError, match="PlainPerson"):
            df_loads(s)

    def test_loose_mode_custom_object_still_works(self, loose):
        """Without strict, the legacy path runs even without expected_type."""
        p = PlainPerson("bob", 25)
        result = df_loads(df_dumps(p))
        assert isinstance(result, PlainPerson)
        assert result.name == "bob"


# ===================================================================
# 11. WIRE FORMAT VERIFICATION
# ===================================================================

class TestWireFormat:

    def test_df_dumps_matches_legacy_json_dumps(self):
        from azure.functions._durable_functions import _serialize_custom_object
        value = {"key": "value", "list": [1, 2, 3]}
        assert df_dumps(value) == json.dumps(value, default=_serialize_custom_object)

    def test_custom_object_produces_legacy_keys(self):
        raw = json.loads(df_dumps(PlainPerson("andy", 99)))
        assert raw == {
            "__class__": "PlainPerson",
            "__module__": __name__,
            "__data__": {"name": "andy", "age": 99},
        }

    def test_scalar_to_json_produces_legacy_keys(self):
        raw = json.loads(df_dumps(ScalarPerson("andy")))
        assert raw == {
            "__class__": "ScalarPerson",
            "__module__": __name__,
            "__data__": "andy",
        }

    def test_nested_object_produces_plain_json_data(self):
        """SmartOrder.to_json serializes Hat explicitly, so __data__
        contains plain JSON -- no nested legacy envelope."""
        raw = json.loads(df_dumps(SmartOrder("gadget", Hat("blue"))))
        assert raw["__class__"] == "SmartOrder"
        assert raw["__data__"] == {"item": "gadget", "hat": {"color": "blue"}}


# ===================================================================
# 12. _get_serialize_default
# ===================================================================

class TestGetSerializeDefault:

    def test_returns_callable(self):
        cb = _get_serialize_default()
        assert callable(cb)

    def test_produces_legacy_dict(self):
        cb = _get_serialize_default()
        result = cb(PlainPerson("a", 1))
        assert result == {
            "__class__": "PlainPerson",
            "__module__": __name__,
            "__data__": {"name": "a", "age": 1},
        }

    def test_strict_returns_none(self, strict):
        cb = _get_serialize_default()
        assert cb is None


# ===================================================================
# 13. ENCODE ERRORS
# ===================================================================

class TestEncodeErrors:

    def test_class_without_to_json(self):
        class NoProtocol:
            pass
        with pytest.raises(TypeError):
            df_dumps(NoProtocol())

    def test_set(self):
        with pytest.raises(TypeError):
            df_dumps({1, 2, 3})

    def test_bytes(self):
        with pytest.raises(TypeError):
            df_dumps(b"hello")


# ===================================================================
# 13b. STRICT-MODE ENCODE
# ===================================================================

class TestStrictEncode:
    """In strict mode, df_dumps rejects non-serializable nested values."""

    def test_primitive(self, strict):
        assert df_dumps(42) == "42"

    def test_string(self, strict):
        assert df_dumps("hello") == '"hello"'

    def test_plain_dict(self, strict):
        assert json.loads(df_dumps({"a": 1})) == {"a": 1}

    def test_custom_object_top_level_ok(self, strict):
        """Top-level custom object is wrapped in envelope."""
        raw = json.loads(df_dumps(PlainPerson("andy", 99)))
        assert raw["__class__"] == "PlainPerson"
        assert raw["__data__"] == {"name": "andy", "age": 99}

    def test_strict_smart_order_data_is_plain_json(self, strict):
        """SmartOrder.to_json returns plain JSON, so encoding succeeds
        and __data__ contains no nested envelopes."""
        raw = json.loads(df_dumps(SmartOrder("gadget", Hat("blue"))))
        assert raw["__class__"] == "SmartOrder"
        assert raw["__data__"] == {"item": "gadget", "hat": {"color": "blue"}}

    def test_strict_naive_order_fails(self, strict):
        """NaiveOrder.to_json returns a Hat instance -- not serializable."""
        with pytest.raises(TypeError):
            df_dumps(NaiveOrder("widget", Hat("red")))

    def test_strict_dict_with_custom_value_fails(self, strict):
        """Plain dict containing a custom object -- not serializable."""
        with pytest.raises(TypeError):
            df_dumps({"person": PlainPerson("a", 1)})

    def test_strict_list_with_custom_value_fails(self, strict):
        """List containing custom objects -- not serializable."""
        with pytest.raises(TypeError):
            df_dumps([PlainPerson("a", 1)])

    def test_loose_dict_with_custom_value_ok(self, loose):
        """In loose mode, nested custom objects are still auto-wrapped."""
        raw = json.loads(df_dumps({"person": PlainPerson("a", 1)}))
        assert raw["person"]["__class__"] == "PlainPerson"


# ===================================================================
# 14. EDGE CASES
# ===================================================================

class TestEdgeCases:

    def test_bool_does_not_become_int(self):
        """bool is a subclass of int -- verify it stays bool."""
        out = df_loads(df_dumps(True))
        assert out is True
        assert isinstance(out, bool)

    def test_none_with_expected_type_nonetype(self, loose):
        assert df_loads(df_dumps(None), expected_type=type(None)) is None

    def test_none_with_expected_type_nonetype_strict(self, strict):
        assert df_loads(df_dumps(None), expected_type=type(None)) is None

    def test_empty_dict_expected_dict(self, loose):
        assert df_loads(df_dumps({}), expected_type=dict) == {}

    def test_empty_list_expected_list(self, strict):
        assert df_loads(df_dumps([]), expected_type=list) == []

    def test_tuple_becomes_list(self):
        """Tuples serialize as JSON arrays -- come back as lists."""
        assert df_loads(df_dumps((1, 2, 3))) == [1, 2, 3]

    def test_tuple_becomes_list_strict(self, strict):
        """Same coercion in strict mode (decoded value is a list)."""
        assert df_loads(df_dumps((1, 2, 3)), expected_type=list) == [1, 2, 3]

    def test_int_dict_keys_become_strings(self):
        decoded = df_loads(df_dumps({1: "one", 2: "two"}))
        assert decoded == {"1": "one", "2": "two"}

    def test_int_dict_keys_become_strings_strict(self, strict):
        """JSON has no int-keyed objects -- coercion happens in strict too."""
        decoded = df_loads(df_dumps({1: "one", 2: "two"}), expected_type=dict)
        assert decoded == {"1": "one", "2": "two"}

    def test_no_expected_type_no_per_call_warning(self, caplog):
        """When expected_type is None, the per-call mismatch / declares
        warnings must not fire (the one-shot advisory is separate and
        emitted at INFO level, not WARNING)."""
        with caplog.at_level(logging.WARNING, logger=df_serialization.__name__):
            df_loads(df_dumps(PlainPerson("a", 1)))
        assert not any("not compatible" in r.message for r in caplog.records)
        assert not any("payload declares" in r.message for r in caplog.records)
