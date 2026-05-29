# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import logging
import os
import sys
import warnings
from typing import Any, Callable, Optional, Union

from . import _abc

logger = logging.getLogger("azure.functions.DurableFunctions")

_STRICT_ENV_VAR = "AZURE_FUNCTIONS_DURABLE_STRICT_TYPING"
_TRUTHY = frozenset({"1", "true", "yes"})
_LEGACY_KEYS = frozenset({"__class__", "__module__", "__data__"})

# One-shot notice flags.  Each becomes True after the corresponding
# advisory has been emitted in this process; tests may reset them.
_loose_codec_notice_emitted = False
_no_expected_type_notice_emitted = False


def _is_strict_mode() -> bool:
    return os.environ.get(_STRICT_ENV_VAR, "").strip().lower() in _TRUTHY


def _notify_loose_codec_used() -> None:
    """Emit a one-time advisory the first time the loose-mode object_hook
    path actually reconstructs a custom object in this process."""
    global _loose_codec_notice_emitted
    if _loose_codec_notice_emitted or _is_strict_mode():
        return
    _loose_codec_notice_emitted = True
    msg = (
        "azure.functions Durable JSON codec reconstructed a custom "
        "object via the loose-mode object_hook path.  Set "
        "AZURE_FUNCTIONS_DURABLE_STRICT_TYPING=1 and supply "
        "expected_type at decode call sites to enable type-validated "
        "deserialization.  This message will not be repeated."
    )
    logger.info(msg)
    warnings.warn(msg, DeprecationWarning, stacklevel=2)


def _notify_no_expected_type() -> None:
    """Emit a one-time advisory the first time df_loads is called in
    loose mode without an expected_type in this process."""
    global _no_expected_type_notice_emitted
    if _no_expected_type_notice_emitted or _is_strict_mode():
        return
    _no_expected_type_notice_emitted = True
    msg = (
        "azure.functions df_loads was called without expected_type.  "
        "Pass the destination type to enable validation and prepare "
        "for strict typing (AZURE_FUNCTIONS_DURABLE_STRICT_TYPING=1).  "
        "This message will not be repeated."
    )
    logger.info(msg)
    warnings.warn(msg, DeprecationWarning, stacklevel=2)


# Utilities
def _serialize_custom_object(obj):
    """Serialize a user-defined object to JSON.

    This function gets called when `json.dumps` cannot serialize
    an object and returns a serializable dictionary containing enough
    metadata to recontrust the original object.

    Parameters
    ----------
    obj: Object
        The object to serialize

    Returns
    -------
    dict_obj: A serializable dictionary with enough metadata to reconstruct
              `obj`

    Exceptions
    ----------
    TypeError:
        Raise if `obj` does not contain a `to_json` attribute
    """
    # 'safety' guard: raise error if object does not
    # support serialization
    if not hasattr(obj, "to_json"):
        raise TypeError(f"class {type(obj)} does not expose a `to_json` "
                        "function")
    # Encode to json using the object's `to_json`
    obj_type = type(obj)
    return {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__,
        "__data__": obj_type.to_json(obj)
    }


def _deserialize_custom_object(obj: dict) -> object:
    """Deserialize a user-defined object from JSON.

    Reconstructs a custom object from a dictionary that carries the
    ``{"__class__", "__module__", "__data__"}`` envelope produced by
    :func:`_serialize_custom_object`.  The class is resolved by looking
    up ``__module__`` in :data:`sys.modules`; modules are never imported
    on demand.

    Parameters
    ----------
    obj: dict
        Dictionary that potentially encodes a custom class.

    Returns
    -------
    object
        Either the original ``obj`` dictionary (if it is not an
        envelope) or the reconstructed custom object.

    Raises
    ------
    ValueError
        If the declared module is not present in ``sys.modules``.
    AttributeError
        If the declared module is loaded but does not define the
        declared class.
    TypeError
        If the resolved class does not expose a ``from_json`` function.
    """
    if ("__class__" in obj) and ("__module__" in obj) and ("__data__" in obj):
        class_name = obj.pop("__class__")
        module_name = obj.pop("__module__")
        obj_data = obj.pop("__data__")

        # Resolve the class from already-loaded modules; this function
        # does not import modules on demand.
        module = sys.modules.get(module_name)
        if module is None:
            raise ValueError(
                f"cannot deserialize custom object: module "
                f"{module_name!r} is not loaded in sys.modules"
            )
        class_ = getattr(module, class_name, None)
        if class_ is None:
            raise AttributeError(
                f"cannot deserialize custom object: class {class_name!r} "
                f"not found in module {module_name!r}"
            )

        if not hasattr(class_, "from_json"):
            raise TypeError(f"class {type(obj)} does not expose a `from_json` "
                            "function")

        # Initialize the object using its `from_json` deserializer
        obj = class_.from_json(obj_data)
        _notify_loose_codec_used()
    return obj


# ---------------------------------------------------------------------------
# Public Durable Functions JSON codec
# ---------------------------------------------------------------------------


def df_dumps(value: Any) -> str:
    """Serialize *value* to a JSON string.

    In **loose mode** (default) this is equivalent to
    ``json.dumps(value, default=_serialize_custom_object)``: nested
    custom objects are wrapped recursively in the
    ``{"__class__", "__module__", "__data__"}`` envelope.

    In **strict mode** (``AZURE_FUNCTIONS_DURABLE_STRICT_TYPING`` set
    to ``1``, ``true`` or ``yes``) only the top-level custom object is
    wrapped; its ``__data__`` payload is serialized as plain JSON
    without a ``default=`` hook.  ``to_json()`` must therefore return
    a value that is natively JSON-serializable, and ``TypeError`` is
    raised if any nested value is not.
    """
    if _is_strict_mode():
        if hasattr(value, "to_json"):
            envelope = _serialize_custom_object(value)
            return json.dumps(envelope)
        # Primitive / plain-JSON value -- serialize without default=.
        return json.dumps(value)
    return json.dumps(value, default=_serialize_custom_object)


def df_loads(s: str, expected_type: Optional[type] = None) -> Any:
    """Deserialize a JSON string, optionally validating against *expected_type*.

    When *expected_type* is ``None``:

    * **Loose mode** (default) runs
      ``json.loads(s, object_hook=_deserialize_custom_object)``.  Custom
      objects whose declaring module is already present in
      ``sys.modules`` are reconstructed; otherwise ``ValueError`` is
      raised.
    * **Strict mode** parses without an ``object_hook``.  A legacy
      custom-object envelope at the top level raises ``TypeError`` --
      the caller must supply ``expected_type`` to deserialize custom
      objects in strict mode.

    When *expected_type* is provided the raw JSON is parsed first
    (without an ``object_hook``) so the payload can be inspected before
    any class lookup.  On a class/module mismatch loose mode logs a
    warning and strict mode raises ``TypeError``.  In loose mode the
    legacy ``object_hook`` path then runs (so nested custom objects are
    also reconstructed); in strict mode the matching custom-object
    payload is reconstructed by calling
    ``expected_type.from_json(raw["__data__"])`` directly.
    """
    if expected_type is not None:
        return _loads_with_expected_type(s, expected_type)

    _notify_no_expected_type()

    if _is_strict_mode():
        return _loads_strict_no_type(s)

    return json.loads(s, object_hook=_deserialize_custom_object)


def _get_serialize_default() -> Optional[Callable]:
    """Return the ``default`` callback for ``json.dumps``.

    Intended for call sites that build their own ``json.dumps``
    invocation (e.g. ``OrchestratorState.to_json_string``) and want to
    honour the active typing mode.  Returns ``_serialize_custom_object``
    in loose mode and ``None`` in strict mode.
    """
    if _is_strict_mode():
        return None
    return _serialize_custom_object


def _loads_strict_no_type(s: str) -> Any:
    """Strict-mode deserialization when no *expected_type* is supplied.

    Parses *s* without an ``object_hook``.  Returns the parsed value
    unchanged for primitive / plain-JSON payloads; raises ``TypeError``
    if the top-level value is a legacy custom-object envelope.
    """
    raw = json.loads(s)
    if _is_legacy_custom_dict(raw):
        raise TypeError(
            "df_loads: strict mode requires expected_type to "
            "deserialize custom-object payloads, but none was provided. "
            f"Payload declares {raw['__module__']}.{raw['__class__']}."
        )
    return raw


def _is_legacy_custom_dict(d: Any) -> bool:
    """Return True if *d* is a dict with legacy custom-object markers."""
    return isinstance(d, dict) and _LEGACY_KEYS.issubset(d)


def _has_json_protocol(cls: type) -> bool:
    """Return True iff *cls* exposes callable ``to_json`` and ``from_json``."""
    return callable(getattr(cls, "to_json", None)) and callable(
        getattr(cls, "from_json", None)
    )


def _is_compatible(value: Any, expected_type: type) -> bool:
    """Best-effort ``isinstance`` check that tolerates generic type hints."""
    try:
        return isinstance(value, expected_type)
    except TypeError:
        # typing constructs like List[int] aren't valid for isinstance.
        return True


def _loads_with_expected_type(s: str, expected_type: type) -> Any:
    """Parse *s* and validate the result against *expected_type*.

    The raw JSON is parsed without an ``object_hook`` so the payload
    shape can be inspected before any class lookup.  In strict mode a
    matching custom-object payload is reconstructed via
    ``expected_type.from_json``; in loose mode the legacy
    ``object_hook`` path runs so nested custom objects inside
    ``__data__`` are also reconstructed.
    """
    raw = json.loads(s)
    strict = _is_strict_mode()

    if _is_legacy_custom_dict(raw):
        class_name = raw["__class__"]
        module_name = raw["__module__"]
        type_matches = (class_name == expected_type.__name__
                        and module_name == expected_type.__module__)

        if not type_matches:
            msg = (
                f"df_loads: payload declares class "
                f"{module_name}.{class_name} but expected "
                f"{expected_type.__module__}.{expected_type.__name__}"
            )
            if strict:
                raise TypeError(msg)
            logger.warning(msg)
            # Fall through to the object_hook path below.

        if strict:
            if not _has_json_protocol(expected_type):
                raise TypeError(
                    f"df_loads: expected_type "
                    f"{expected_type.__module__}.{expected_type.__name__} "
                    f"does not expose from_json"
                )
            return expected_type.from_json(raw["__data__"])

        # Loose mode -- use the object_hook path so nested custom
        # objects inside __data__ are also reconstructed.
        return json.loads(s, object_hook=_deserialize_custom_object)

    # Primitive / plain-JSON payload -- validate the Python type.
    if not _is_compatible(raw, expected_type):
        msg = (
            f"df_loads: deserialized value ({type(raw).__name__}) is not "
            f"compatible with expected type {expected_type}"
        )
        if strict:
            raise TypeError(msg)
        logger.warning(msg)

    if strict:
        return raw
    # Loose mode -- use the object_hook path so nested custom objects
    # inside dicts/lists are reconstructed.
    return json.loads(s, object_hook=_deserialize_custom_object)


class OrchestrationContext(_abc.OrchestrationContext):
    """A durable function orchestration context.

    :param str body:
        The body of orchestration context json.
    """

    def __init__(self,
                 body: Union[str, bytes]) -> None:
        if isinstance(body, str):
            self.__body = body
        if isinstance(body, bytes):
            self.__body = body.decode('utf-8')

    @property
    def body(self) -> str:
        return self.__body

    def __repr__(self):
        return (
            f'<azure.OrchestrationContext '
            f'body={self.body}>'
        )

    def __str__(self):
        return self.__body


class EntityContext(_abc.OrchestrationContext):
    """A durable function entity context.

    :param str body:
        The body of orchestration context json.
    """

    def __init__(self,
                 body: Union[str, bytes]) -> None:
        if isinstance(body, str):
            self.__body = body
        if isinstance(body, bytes):
            self.__body = body.decode('utf-8')

    @property
    def body(self) -> str:
        return self.__body

    def __repr__(self):
        return (
            f'<azure.EntityContext '
            f'body={self.body}>'
        )

    def __str__(self):
        return self.__body
