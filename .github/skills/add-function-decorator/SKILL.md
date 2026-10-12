---
name: add-function-decorator
description: 'Add or extend an Azure Functions Python SDK decorator or binding. Use when implementing decorator arguments, snake_case APIs, enums and string parsing, public exports, pydocs, binding metadata serialization, converters, or decorator regression tests in this repository.'
---

# Add or extend a function decorator

Implement decorators using this SDK's existing binding, function-builder, and
serialization conventions. This workflow also applies to adding arguments to an
existing decorator without breaking existing users.

## 1. Review the reference PRs and current implementation

Review the **Files changed** tabs, not only the PR descriptions:

- [PR #339: add connector decorator](https://github.com/Azure/azure-functions-python-library/pull/339/files)
  demonstrates the complete path from trigger binding to decorator, converter,
  registration, and tests. It touched seven files:
  [public exports and registration](../../../azure/functions/__init__.py),
  [connector converter](../../../azure/functions/connectors.py),
  [connector binding](../../../azure/functions/decorators/connectors.py),
  [binding constants](../../../azure/functions/decorators/constants.py),
  [decorator API](../../../azure/functions/decorators/function_app.py),
  [binding tests](../../../tests/decorators/test_connector.py), and
  [converter and integration tests](../../../tests/test_connector.py).
- [PR #330: MCP prompt trigger](https://github.com/Azure/azure-functions-python-library/pull/330/files)
  demonstrates typed snake_case arguments, pydocs, forwarding to a binding,
  public helper exports, and structured argument serialization. It touched
  eight files: both package initializers, binding constants, the decorator API,
  both MCP modules, and both MCP test modules.

Use these PRs as precedent, not immutable templates. Inspect the current checkout
because implementations and requirements may have changed since those PRs.
If the PR diff cannot be retrieved, state that limitation and use local evidence;
do not claim to have reviewed unavailable content.

Read the relevant binding module, its decorator method, tests, and the shared
[binding infrastructure](../../../azure/functions/decorators/core.py) and
[serialization utilities](../../../azure/functions/decorators/utils.py).
Use a comparable trigger/input/output binding as a second reference.

Before editing:

- Inspect the working tree and preserve unrelated user changes.
- Confirm extension-side binding type, JSON property names, types, required
  fields, conditional requirements, defaults, and accepted enum values.
- Distinguish host defaults from SDK defaults. Do not guess extension behavior.
- Record a short plan and establish a focused test baseline.
- When available, use Pylance references or signature compatibility checks to
  identify existing callers before changing a Python API.
- For Azure work, consult applicable Azure best practices when available.

## 2. Define the public Python API

- Use **snake_case** for decorator and binding constructor parameters:
  `delivery_mode`, `trigger_config_name`, `max_batch_size`, and
  `target_pending_event_threshold`, not their camelCase JSON counterparts.
- The decorator uses `arg_name`; pass it to the binding constructor as `name`.
- Give known extension fields explicit, accurately typed parameters instead of
  hiding them in `**kwargs`. Retain `**kwargs` for additional binding fields.
- Use `Optional[T] = None` for fields that may be omitted. Prefer omission when
  the host owns the default; do not eagerly insert a default into JSON.
- Preserve existing positional parameter order. In particular, extending
  `connector_trigger` must not displace its second argument, `data_type`.
- Follow the surrounding `typing` style and supported Python versions rather
  than introducing unrelated annotation modernization.
- Conditional requirements need optional signature parameters: Poll-only
  settings must not become mandatory for Webhook callers.

## 3. Add enums and support strings

- Reuse existing enums, such as `Cardinality` and `DataType`, where appropriate.
- Add shared public binding enums to
  [core.py](../../../azure/functions/decorators/core.py); keep binding-specific
  types near the binding when that matches neighboring implementations.
- Use `StringifyEnum` when participating in the SDK's JSON serialization.
  Name members in uppercase and document the enum and each member.
- Public enum parameters should accept `Optional[Union[EnumType, str]]` when
  string input is supported. Normalize with `parse_singular_param_to_enum`;
  do not implement a separate string parser.
- The helper looks up `param.upper()` by **member name**, preserves enum objects,
  returns `None` for omission, and raises `KeyError` for invalid strings. Values
  with different spelling from member names require deliberate mapping and tests.
- Normalize before enum comparisons and conditional validation. If direct binding
  construction also supports strings, normalize in that constructor as well;
  otherwise a string such as `"Poll"` can bypass a `DeliveryMode.POLL` check.
- Verify the **actual serialized string**, not only `.value`. The shared
  `StringifyEnum.__str__` returns the member name, and
  `StringifyEnumJsonEncoder` serializes `str(enum)`. A mixed-case wire value may
  therefore require a narrowly scoped `__str__` override, as with `DeliveryMode`
  emitting `"Poll"` and `"Webhook"`. Do not change shared enum serialization to
  fix a single binding.
- Preserve existing `Cardinality` serialization; do not replace it with an
  `is_batched` field merely because the extension exposes an equivalent option.
- Export public enums/helpers through
  [decorators/__init__.py](../../../azure/functions/decorators/__init__.py) and
  [functions/__init__.py](../../../azure/functions/__init__.py), including their
  `__all__` entries. Test access through `azure.functions`.

## 4. Implement the binding and decorator

### Binding class

- Add a binding type constant to
  [constants.py](../../../azure/functions/decorators/constants.py) only when the
  binding type is new. Implement `get_binding_name()` with the exact host name.
- Inherit from `Trigger`, `InputBinding`, or `OutputBinding` as appropriate.
- Assign each explicit field to its same-named snake_case instance attribute,
  then call the base constructor with `name`, `data_type`, and other applicable
  common fields.
- `Binding.get_dict_repr()` inspects constructor parameters and converts their
  names to camelCase. `BuildDictMeta` tracks parameters, retains additional
  kwargs, and removes `None` recursively. Prefer these mechanisms over custom
  JSON assembly. Keep `**kwargs` in the constructor signature.
- Preserve valid falsy metadata (`0`, `False`, empty collections) unless the
  extension contract explicitly rejects it. Check `is None` for omission rather
  than treating every falsy value as absent.
- Put conditional required-field checks in the binding so direct construction
  and decorator usage have consistent behavior. Raise an actionable `ValueError`
  listing missing snake_case parameters. Validate only the applicable mode.
- Do not invent numeric ranges or restrictions. Confirm extension requirements
  before enforcing positive values, nonempty strings, or mutually exclusive fields.

### Decorator method

- Add or extend the appropriate API method in
  [function_app.py](../../../azure/functions/decorators/function_app.py).
- Follow the existing `@self._configure_function_builder` wrapper pattern and
  the relevant `fb.add_trigger`, `fb.add_binding`, or setting method.
- Forward **every** explicit parameter to the binding, plus `**kwargs`.
- Parse `data_type` and other enum parameters using the shared helpers.
- Only add structured serialization when the extension contract requires it.
  PR #330's `PromptArgument` list-to-JSON conversion is such a case; primitive
  scalar binding fields do not need that special handling.

### Runtime converters

- Metadata-only argument changes do not automatically require converter changes.
  Inspect the payload contract and existing converter first.
- For a genuinely new binding, add/register a converter in the runtime module
  when required, import it from the package initializer for registration, and
  test input annotations, decoding, encoding, and implicit-output behavior.
- If batching changes the runtime payload shape, confirm converter compatibility
  rather than assuming a `cardinality` metadata change is sufficient.

## 5. Write pydocs alongside the implementation

Use the existing decorator docstring structure:

- Explain what binding is added to `FunctionBuilder` and how it participates in
  worker indexing / legacy function metadata.
- Describe triggering or input/output behavior and any relevant official reference.
- Document **every** argument with `:param snake_case_name:`, including
  `arg_name`, `data_type`, and `kwargs`; include `:return: Decorator function.`
- Explain accepted enum/string forms, omission behavior, host-owned defaults,
  conditional requirements, batching, and app-setting expressions where supported.
- Document new public enums, members, and helper objects. Keep documentation
  accurate to the extension contract rather than inferring behavior from names.
- Follow repository formatting: four spaces and a 100-character maximum line
  length, including imports and wrapped parameter descriptions.
- Check documentation stubs and examples for relevant public API updates; do not
  modify unrelated or stale artifacts just because they exist.

## 6. Add regression tests at both layers

Extend the matching modules under `tests/decorators/` and `tests/`:

1. Binding name, direction, minimal construction, and complete dictionary output.
2. Exact camelCase keys for explicit parameters and arbitrary snake_case kwargs.
3. Omitted `None` fields and preservation of meaningful falsy values.
4. Enum objects, case-insensitive string forms, invalid strings, and public exports.
5. Direct binding construction and decorator calls with string enum parameters.
6. Each conditionally required field missing individually, plus an error listing
   all missing fields; other modes must work without those fields.
7. Both cardinalities where supported and omission of optional batching settings.
8. Existing positional calls, previous minimal usage, and unchanged kwargs support.
9. End-to-end metadata using `FunctionApp.get_functions()` and
   `json.loads(function.get_function_json())`. Assert exact wire values and keys,
   not only enum-valued dictionaries from `get_dict_repr()`.
10. Converter behavior when the converter or payload contract changes.

Use `subTest` for case matrices where useful. Keep tests deterministic and avoid
requiring live Azure resources for decorator metadata verification.

## 7. Validate and report

- Configure/use the repository's selected Python environment; do not assume the
  terminal's unqualified `python` is that interpreter.
- If dependencies are missing, install the declared development extra (`.[dev]`)
  into the chosen environment; do not rewrite dependency constraints just to
  work around a local missing package.
- Run focused binding/decorator/converter tests, then the full test suite.
- Use [test_code_quality.py](../../../tests/test_code_quality.py) as the source
  of truth for lint and pydoc checks. It runs flake8 with the repository
  [.flake8](../../../.flake8) configuration, ignores `D` for general lint, and
  selects `D` for pydocs on the decorator API. Do not suppress new violations.
- Check editor/Pylance diagnostics, syntax, signature compatibility, and
  `git diff --check`. A clean editor report does not replace runtime tests.
- Read actual terminal results and preserve failing test exit codes when chaining
  commands; a successful trailing Git command must not mask failed tests.
- Review the final diff for unintended files, missing exports, undocumented
  arguments, duplicate serialization logic, and compatibility regressions.
- Report the API change, validation behavior, test results, and any skipped or
  unavailable checks. Do not claim live extension compatibility from SDK unit
  tests alone.