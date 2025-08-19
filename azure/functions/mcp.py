import typing

from . import meta


class MCPToolRequest:
    """Wrapper for MCP tool trigger payload providing raw & parsed access."""

    def __init__(self, raw: typing.Any):
        self.raw = raw
        self.json = None
        if isinstance(raw, str):
            try:
                from ._jsonutils import json as _json
                self.json = _json.loads(raw)
            except Exception:
                self.json = None
        elif isinstance(raw, dict):
            # If raw is already a dict, use it as the parsed JSON
            self.json = raw


class MCPToolTriggerConverter(meta.InConverter, binding='mcpToolTrigger',
                              trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (MCPToolRequest, str))

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata):
        # Handle different data types appropriately
        if data.type == 'json':
            # If it's already parsed JSON, use the value directly
            val = data.value
        elif data.type == 'string':
            # If it's a string, use it as-is
            val = data.value
        else:
            # Fallback to python_value for other types
            val = data.python_value if hasattr(data, 'python_value') else data.value
        return MCPToolRequest(val)


class MCPToolInputConverter(meta.InConverter, binding='mcpToolInput'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, MCPToolRequest))

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata):
        val = data.python_value if hasattr(data, 'python_value') else data.value
        return val


class MCPToolOutputConverter(meta.OutConverter, binding='mcpToolOutput'):

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str,))

    @classmethod
    def encode(cls, obj: typing.Any, *, expected_type: typing.Optional[type]):
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)
        raise NotImplementedError
