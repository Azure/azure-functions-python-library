# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""JSON serialization helpers for Durable Functions custom objects.

This module exposes a registry-based, symmetric encode/decode pipeline
for round-tripping user-defined classes through JSON, plus back-compat
shims for the historical ``default=`` / ``object_hook=`` helper pair.

The new pipeline (``to_json_string`` / ``from_json_string``) only
reconstructs classes that have been registered via
``register_durable_serializable_type``; dicts whose shape would collide
with a marker are escaped on encode and restored on decode. The legacy
shims (``_serialize_custom_object`` / ``_deserialize_custom_object``)
preserve the original wire shape for back-compat but resolve target
classes only through the registry or already-loaded modules; no module
is imported during decoding.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import warnings
from threading import Lock
from typing import Any, Dict, Type, Union

from . import _abc


_OBJ_KEY = "__azfunc_obj__"
_ESC_KEY = "__azfunc_escaped__"
_LEGACY_KEYS = ("__class__", "__module__", "__data__")

_registered_types: Dict[str, Type] = {}
_registry_lock = Lock()

_STRICT_LEGACY = os.environ.get(
    "AZURE_FUNCTIONS_DURABLE_STRICT_LEGACY_DESERIALIZE", ""
).lower() in ("1", "true", "yes")

_logger = logging.getLogger("azure.functions.DurableFunctions")


def register_durable_serializable_type(cls: Type) -> Type:
    """Register ``cls`` as eligible for JSON round-tripping.

    Usable as a decorator. Idempotent for the same class; raises
    ``ValueError`` if a different class is already registered under the
    same module-qualified name. The class must define both ``to_json``
    and ``from_json``.
    """
    if not (hasattr(cls, "to_json") and hasattr(cls, "from_json")):
        raise TypeError(
            f"{cls!r} must define both `to_json` and `from_json` "
            "to be registered as a durable-serializable type."
        )
    key = f"{cls.__module__}.{cls.__qualname__}"
    with _registry_lock:
        prior = _registered_types.get(key)
        if prior is not None and prior is not cls:
            raise ValueError(
                f"A different class is already registered as {key!r}"
            )
        _registered_types[key] = cls
    return cls


def _is_single_key(d: dict, key: str) -> bool:
    return len(d) == 1 and next(iter(d)) == key


def _is_legacy_marker(d: dict) -> bool:
    return all(k in d for k in _LEGACY_KEYS)


def _encode(value: Any) -> Any:
    """Walk ``value`` and convert registered instances to markers.

    Dicts whose shape would collide with a current or legacy marker are
    wrapped under ``_ESC_KEY`` so that decode can restore them as-is.
    """
    if isinstance(value, dict):
        if (_is_single_key(value, _OBJ_KEY)
                or _is_single_key(value, _ESC_KEY)
                or _is_legacy_marker(value)):
            return {_ESC_KEY: {k: _encode(v) for k, v in value.items()}}
        return {k: _encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_encode(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "to_json"):
        key = f"{type(value).__module__}.{type(value).__qualname__}"
        if key not in _registered_types:
            raise TypeError(
                f"{type(value)!r} has `to_json` but is not registered "
                "as a durable-serializable type. "
                "Call register_durable_serializable_type(cls) at app startup."
            )
        return {_OBJ_KEY: {"t": key, "d": _encode(type(value).to_json(value))}}
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")


def _resolve_loaded_class(module_name: str, class_name: str):
    """Return a class named ``class_name`` from an already-loaded module.

    Returns ``None`` unless every check passes:

    * ``module_name`` is present in ``sys.modules`` (no import is performed),
    * the attribute is a real ``type``,
    * ``from_json`` is defined directly on the class as a
      ``classmethod`` or ``staticmethod`` and is callable,
    * ``to_json`` is also defined,
    * the class's ``__module__`` matches ``module_name``.
    """
    module = sys.modules.get(module_name)
    if module is None:
        return None
    cls = getattr(module, class_name, None)
    if cls is None or not isinstance(cls, type):
        return None
    raw = cls.__dict__.get("from_json")
    if not isinstance(raw, (classmethod, staticmethod)):
        return None
    if not callable(getattr(cls, "from_json", None)):
        return None
    if not hasattr(cls, "to_json"):
        return None
    if getattr(cls, "__module__", None) != module_name:
        return None
    return cls


def _legacy_resolve(mod_name: str, cls_name: str):
    """Resolve a legacy ``__class__/__module__/__data__`` marker.

    Consults the registry first; falls back to ``_resolve_loaded_class``
    unless strict mode is enabled. Never imports a module.
    """
    cls = _registered_types.get(f"{mod_name}.{cls_name}")
    if cls is not None:
        return cls
    if _STRICT_LEGACY:
        return None
    return _resolve_loaded_class(mod_name, cls_name)


def _warn_legacy_hit(mod_name: str, cls_name: str, *, resolved: bool) -> None:
    """Emit a log warning and ``DeprecationWarning`` for legacy decode."""
    if resolved:
        msg = (
            f"Durable Functions reconstructed {mod_name}.{cls_name} via the "
            "legacy custom-object marker. Migrate to "
            "azure.functions._durable_functions."
            "register_durable_serializable_type(cls); the legacy shape "
            "will be removed in the next major version."
        )
    else:
        msg = (
            f"Durable Functions saw a legacy custom-object marker for "
            f"{mod_name}.{cls_name} but could not resolve it. "
            "Returning as dict. Either register the class with "
            "register_durable_serializable_type(cls), or import the "
            "module at app startup and ensure the class defines "
            "to_json/from_json (from_json must be a classmethod or "
            "staticmethod). The legacy shape will be removed in the next "
            "major version."
        )
    _logger.warning(msg)
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


def _decode(value: Any, *, accept_legacy: bool = False) -> Any:
    """Inverse of :func:`_encode`.

    When ``accept_legacy`` is true, dicts in the
    ``__class__/__module__/__data__`` shape are also recognised and
    resolved via :func:`_legacy_resolve`. Unknown markers are returned
    as plain dicts.
    """
    if isinstance(value, dict):
        if _is_single_key(value, _OBJ_KEY):
            marker = value[_OBJ_KEY]
            if not (isinstance(marker, dict)
                    and isinstance(marker.get("t"), str)
                    and "d" in marker):
                return value
            cls = _registered_types.get(marker["t"])
            decoded_data = _decode(marker["d"], accept_legacy=accept_legacy)
            if cls is None:
                return {_OBJ_KEY: {"t": marker["t"], "d": decoded_data}}
            return cls.from_json(decoded_data)

        if _is_single_key(value, _ESC_KEY):
            inner = value[_ESC_KEY]
            if isinstance(inner, dict):
                return {k: _decode(v, accept_legacy=accept_legacy)
                        for k, v in inner.items()}
            return inner

        if accept_legacy and _is_legacy_marker(value):
            cls_name = value.get("__class__")
            mod_name = value.get("__module__")
            data = value.get("__data__")
            if isinstance(cls_name, str) and isinstance(mod_name, str):
                cls = _legacy_resolve(mod_name, cls_name)
                if cls is not None:
                    _warn_legacy_hit(mod_name, cls_name, resolved=True)
                    return cls.from_json(
                        _decode(data, accept_legacy=accept_legacy)
                    )
                _warn_legacy_hit(mod_name, cls_name, resolved=False)
            return {k: _decode(v, accept_legacy=accept_legacy)
                    for k, v in value.items()}

        return {k: _decode(v, accept_legacy=accept_legacy)
                for k, v in value.items()}

    if isinstance(value, list):
        return [_decode(v, accept_legacy=accept_legacy) for v in value]
    return value


def to_json_string(obj: Any) -> str:
    """Serialize ``obj`` to a JSON string using the symmetric pipeline."""
    return json.dumps(_encode(obj))


def from_json_string(s: str, *, accept_legacy: bool = False) -> Any:
    """Deserialize a JSON string produced by :func:`to_json_string`.

    Set ``accept_legacy=True`` to also decode values written by older
    library versions in the ``__class__/__module__/__data__`` shape.
    """
    return _decode(json.loads(s), accept_legacy=accept_legacy)


def _serialize_custom_object(obj):
    """Back-compat ``default=`` callback for ``json.dumps``.

    Emits the legacy ``__class__/__module__/__data__`` shape so older
    consumers continue to decode correctly. Only registered classes are
    accepted.
    """
    key = f"{type(obj).__module__}.{type(obj).__qualname__}"
    if key not in _registered_types:
        raise TypeError(
            f"{type(obj)!r} is not a registered durable-serializable type."
        )
    if not hasattr(obj, "to_json"):
        raise TypeError(f"{type(obj)!r} does not expose `to_json`.")
    return {
        "__class__": type(obj).__qualname__,
        "__module__": type(obj).__module__,
        "__data__": type(obj).to_json(obj),
    }


def _deserialize_custom_object(obj: dict) -> object:
    """Back-compat ``object_hook`` callback for ``json.loads``.

    Resolves target classes via :func:`_legacy_resolve` (registry, then
    already-loaded modules in non-strict mode). No module is imported.
    Unrecognised markers are returned as plain dicts.
    """
    if not all(k in obj for k in _LEGACY_KEYS):
        return obj
    cls_name = obj.get("__class__")
    mod_name = obj.get("__module__")
    if not (isinstance(cls_name, str) and isinstance(mod_name, str)):
        return obj
    cls = _legacy_resolve(mod_name, cls_name)
    if cls is None:
        _warn_legacy_hit(mod_name, cls_name, resolved=False)
        return obj
    _warn_legacy_hit(mod_name, cls_name, resolved=True)
    data = obj["__data__"]
    obj.pop("__class__")
    obj.pop("__module__")
    obj.pop("__data__")
    return cls.from_json(data)


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
