# Feature Spec: Centralized Durable Functions Serialization in azure-functions-python-library

**Status:** Draft  
**Author:** (Durable Functions team)  
**Target repo:** `Azure/azure-functions-python-library`  
**Target files:** `azure/functions/_durable_functions.py`, `azure/functions/durable_functions.py`  
**Upstream consumer:** `Azure/azure-functions-durable-python` (will drop its local `df_serialization.py` and import from here)

---

## 1. Motivation

The `_serialize_custom_object` / `_deserialize_custom_object` pair in
`azure/functions/_durable_functions.py` is the canonical codec for Durable
Functions custom-object payloads.  Today every call site (the Durable SDK's
action classes, context objects, entity state, **and** the activity trigger
converters in `azure/functions/durable_functions.py`) independently calls
`json.dumps(..., default=_serialize_custom_object)` /
`json.loads(..., object_hook=_deserialize_custom_object)`.

Problems:

1. **No type validation.** `_deserialize_custom_object` unconditionally calls
   `importlib.import_module(module_name)` on whatever `__module__` string is in
   the payload — there is no check that the declared class matches what the
   caller expects.

2. **Security concern.** An attacker-controlled payload can embed arbitrary
   `__module__` / `__class__` values, causing `import_module` to load any
   installed module and call its `from_json`.  This is especially relevant for
   `ActivityTriggerConverter.decode` and `LegacyActivityTriggerConverter.decode`
   which deserialize inbound trigger data with no gating.

3. **No single entry point.** Serialization logic is scattered; adding
   cross-cutting behavior (logging, validation, strict mode) requires touching
   every call site.

## 2. Proposed API

Add two public functions to `azure/functions/_durable_functions.py`:

```python
def df_dumps(value: Any) -> str:
    """Serialize *value* to a JSON string using the Durable Functions convention.

    In loose mode (default), equivalent to
    ``json.dumps(value, default=_serialize_custom_object)``.

    In strict mode, the top-level custom object is wrapped in the
    legacy envelope but its ``to_json()`` output is serialized as
    plain JSON (no ``default=`` hook).  Primitives and plain
    containers are also serialized without ``default=``.
    A ``TypeError`` is raised if any nested value is not natively
    JSON-serializable.
    """

def df_loads(
    s: str,
    expected_type: Optional[type] = None,
) -> Any:
    """Deserialize a JSON string, optionally validating against *expected_type*.

    When *expected_type* is None, behaves identically to
    ``json.loads(s, object_hook=_deserialize_custom_object)``.

    When *expected_type* is provided, the raw JSON is parsed first
    (without ``object_hook``) so the payload can be inspected before
    ``import_module`` fires.  Behavior then depends on the typing mode:

    * **Loose mode** (default) — logs a warning on type mismatch, then
      falls through to the legacy ``object_hook`` path.
    * **Strict mode** — raises ``TypeError`` on mismatch.  For custom-
      object payloads, calls ``expected_type.from_json(raw["__data__"])``
      directly without ``import_module``.  Opted in via the
      ``AZURE_FUNCTIONS_DURABLE_STRICT_TYPING`` environment variable.
    """
```

### 2.1 Wire format — Loose mode

**No change.** `df_dumps` produces the same JSON that
`json.dumps(value, default=_serialize_custom_object)` produces today:
- Builtins → plain JSON
- Custom objects with `to_json` → `{"__class__": ..., "__module__": ..., "__data__": ...}`
- Nested custom objects are recursively wrapped via the `default=` hook

### 2.1.1 Wire format — Strict mode

`df_dumps` in strict mode:
- Top-level custom objects with `to_json` → same `{"__class__", "__module__", "__data__"}` envelope
- But `__data__` is the **plain JSON** output of `to_json()` — serialized **without** `default=_serialize_custom_object`
- Primitives and plain containers → serialized without `default=`
- Any nested value that is not natively JSON-serializable → `TypeError` at encode time

This means `to_json()` must produce a value that `json.dumps` can handle
natively.  Nested custom objects must be serialized explicitly inside
`to_json()` (e.g., call `Hat.to_json(self.hat)` rather than returning
`self.hat` directly).  This is a **deliberate breaking change** for strict
mode — it ensures no `__module__` strings reach storage at nested levels,
eliminating the `import_module` attack surface entirely.

### 2.2 `df_loads` without `expected_type` — Loose mode

Behaves identically to `json.loads(s, object_hook=_deserialize_custom_object)`.
This is the backward-compatible path for call sites that have no type info.

### 2.2.1 `df_loads` without `expected_type` — Strict mode

Parses without `object_hook` so `import_module` is **never** called.  If the
top-level value is a legacy custom-object dict, raises `TypeError` — the caller
must supply an `expected_type` to deserialize custom objects in strict mode.
Primitive / plain-JSON payloads are returned as-is (no security risk, no
`import_module` involved).

This ensures that enabling strict mode surfaces every untyped call site as a
loud failure rather than silently falling through to `import_module`.

### 2.3 `df_loads` with `expected_type` — Loose mode (default)

1. Parse `s` with plain `json.loads(s)` (no `object_hook`) → `raw`.
2. If `raw` is a legacy custom-object dict (`{"__class__", "__module__", "__data__"}` ⊆ keys):
   a. Compare `raw["__class__"]` / `raw["__module__"]` against `expected_type.__name__` / `expected_type.__module__`.
   b. On mismatch → `logger.warning(...)`.
   c. Fall through to `json.loads(s, object_hook=_deserialize_custom_object)` (legacy behavior preserved).
3. If `raw` is a primitive/plain-JSON value:
   a. Best-effort `isinstance(raw, expected_type)` check (tolerate `TypeError` for `typing` generics).
   b. On mismatch → `logger.warning(...)`.
   c. Fall through to `json.loads(s, object_hook=_deserialize_custom_object)` so nested custom objects in dicts/lists are still reconstructed.

### 2.4 `df_loads` with `expected_type` — Strict mode

Opted in by setting `AZURE_FUNCTIONS_DURABLE_STRICT_TYPING` to `1`, `true`, or `yes`.

1. Parse `s` with plain `json.loads(s)` (no `object_hook`) → `raw`.
2. If `raw` is a legacy custom-object dict:
   a. Compare class/module as above.
   b. On mismatch → `raise TypeError(...)`.
   c. Verify `expected_type` has callable `from_json`; if not → `raise TypeError(...)`.
   d. Return `expected_type.from_json(raw["__data__"])` — **`import_module` is never called**.
   e. Because `df_dumps` in strict mode produces plain-JSON `__data__` (no
      nested envelopes), `from_json` receives clean data.  If consuming
      legacy (loose-encoded) payloads, nested `{"__class__", ...}` dicts
      may still appear — `from_json` should handle both shapes.
3. If `raw` is a primitive/plain-JSON value:
   a. `isinstance` check as above.
   b. On mismatch → `raise TypeError(...)`.
   c. Return `raw` directly (no `object_hook` pass).

### 2.5 Environment variable

| Variable | Values | Default |
|---|---|---|
| `AZURE_FUNCTIONS_DURABLE_STRICT_TYPING` | `1`, `true`, `yes` (case-insensitive, stripped) | unset = loose mode |

This is the same env var already used by the Durable SDK's interim implementation.

## 3. Internal helpers to expose

The Durable SDK currently imports `_serialize_custom_object` directly for
`OrchestratorState.to_json_string` (which builds its own `json.dumps` call).
To avoid reaching into private names, also expose:

```python
def _get_serialize_default() -> Callable:
    """Return the ``default`` callback for ``json.dumps``.

    For use in call sites that build their own ``json.dumps`` invocation
    (e.g. ``OrchestratorState.to_json_string``).
    """
    return _serialize_custom_object
```

Alternatively, if the preference is to keep the public surface minimal, the
Durable SDK can continue importing `_serialize_custom_object` directly — it
already does so today.

## 4. Converter changes

### 4.1 `ActivityTriggerConverter.decode` and `LegacyActivityTriggerConverter.decode`

Both converters currently do:

```python
callback = _durable_functions._deserialize_custom_object
result = json.loads(data.value, object_hook=callback)
```

Change to:

```python
result = _durable_functions.df_loads(data.value)
```

This is behavior-identical in the default (no `expected_type`) case.  A future
enhancement could pass the activity function's input type annotation as
`expected_type` if the converter framework makes it available (see §6).

### 4.2 `ActivityTriggerConverter.encode` and `LegacyActivityTriggerConverter.encode`

Both converters currently do:

```python
callback = _durable_functions._serialize_custom_object
result = json.dumps(obj, default=callback)
```

Change to:

```python
result = _durable_functions.df_dumps(obj)
```

### 4.3 Error handling

The converters' existing `try/except json.JSONDecodeError` and
`try/except TypeError` blocks remain unchanged — they wrap the `df_loads` /
`df_dumps` calls exactly as they wrap the current `json.loads` / `json.dumps`
calls.

## 5. Implementation guidance

### 5.1 Placement

All new code goes in `azure/functions/_durable_functions.py`, next to the
existing `_serialize_custom_object` / `_deserialize_custom_object` functions.
The existing functions remain for backward compatibility (they are still called
internally by `df_loads` in loose mode).

### 5.2 Logging

Use `logging.getLogger("azure.functions._durable_functions")`.

### 5.3 Reference implementation

The Durable SDK's interim implementation is at:

```
azure-functions-durable-python/azure/durable_functions/models/utils/df_serialization.py
```

(branch: the PR that adds this spec)

That file is ~180 lines and contains the complete logic for `df_dumps`,
`df_loads`, `_loads_with_expected_type`, `_is_strict_mode`, `_is_legacy_custom_dict`,
`_has_json_protocol`, and `_is_compatible`.  The implementation should be
moved here essentially verbatim, with the only difference being that
`_serialize_custom_object` and `_deserialize_custom_object` are local
rather than imported.

### 5.4 Strict-mode serialization contract

In strict mode, the `to_json` / `from_json` contract is symmetric:

> **`to_json()`** must return a value that is natively JSON-serializable —
> dicts, lists, strings, numbers, bools, None.  Nested custom objects must
> be serialized explicitly (e.g., call `Hat.to_json(self.hat)`).
>
> **`from_json(data)`** receives exactly what `to_json()` produced — plain
> JSON data with no `{"__class__", "__module__", "__data__"}` markers at
> any nesting level.  Reconstruct nested objects using their `from_json`.

Example:

```python
class Order:
    @staticmethod
    def to_json(obj):
        return {
            "item": obj.item,
            "hat": Hat.to_json(obj.hat),   # explicit — not obj.hat
        }

    @staticmethod
    def from_json(data):
        return Order(
            item=data["item"],
            hat=Hat.from_json(data["hat"]),  # symmetric
        )
```

If the application may also receive legacy (loose-encoded) payloads during
a rollout, `from_json` can check for both shapes:

```python
    @staticmethod
    def from_json(data):
        hat_data = data["hat"]
        if isinstance(hat_data, Hat):
            hat = hat_data           # loose mode: object_hook already fired
        else:
            hat = Hat.from_json(hat_data)  # strict mode: plain dict
        return Order(item=data["item"], hat=hat)
```

## 6. Future work (out of scope for this PR)

- **Pass `expected_type` into converter `decode`:** The `InConverter.decode`
  interface currently only receives `data` and `trigger_metadata`.  Adding an
  optional `expected_type` kwarg (sourced from the function's parameter type
  annotation) would let `ActivityTriggerConverter.decode` call
  `df_loads(data.value, expected_type=pytype)` — closing the last
  unprotected `import_module` path.  This requires a change to the worker's
  converter dispatch in `azure-functions-python-worker`.

- **Deprecate direct use of `_serialize_custom_object` /
  `_deserialize_custom_object`:** Once `df_dumps` / `df_loads` are available,
  the underscore-prefixed functions become internal implementation details.

## 7. Testing

### 7.1 Unit tests to add (in the functions SDK repo)

1. **`df_dumps` round-trips** — primitives, custom objects with `to_json`, nested structures.
2. **`df_loads` without expected_type (loose)** — identical to legacy `json.loads(s, object_hook=...)`.
3. **`df_loads` without expected_type (strict), primitive payload** — returns raw value, no `import_module`.
4. **`df_loads` without expected_type (strict), custom-object payload** — raises `TypeError`.
3. **`df_loads` loose mode with matching type** — no warning, correct object returned.
4. **`df_loads` loose mode with mismatched type** — warning logged, legacy path still runs.
5. **`df_loads` strict mode with matching type** — `from_json` called directly, `import_module` never called.
6. **`df_loads` strict mode with mismatched type** — `TypeError` raised.
7. **`df_loads` strict mode, type lacks `from_json`** — `TypeError` raised.
8. **`df_loads` with primitive payload and expected_type** — isinstance validation.
9. **`df_loads` with `typing` generics as expected_type** — no crash (isinstance tolerance).
10. **Converter integration** — `ActivityTriggerConverter.decode` / `.encode` use `df_loads` / `df_dumps`.

### 7.2 Existing tests in the Durable SDK

The Durable SDK has 101 round-trip / validation tests in
`tests/utils/test_df_serialization.py` that exercise the exact same logic.
These can serve as a reference / be ported.

## 8. Migration plan

1. **This PR (functions SDK):** Add `df_dumps`, `df_loads` to `_durable_functions.py`.
   Update the four converter methods to use them.  Ship as a new patch/minor.

2. **Same PR (Durable SDK) — updated after functions SDK ships:** Remove
   `azure/durable_functions/models/utils/df_serialization.py`.  Change all
   imports from `.utils.df_serialization` to
   `azure.functions._durable_functions`.  Add `azure-functions>=<new_version>`
   to `install_requires`.  This is the same in-progress Durable SDK PR — it
   will be rebased to consume the functions SDK's definitive implementation
   before merging.

3. **Future (worker):** Extend `InConverter.decode` to accept `expected_type`,
   enabling `ActivityTriggerConverter` to pass the function's input annotation
   through to `df_loads`.
