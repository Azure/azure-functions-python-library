# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import typing
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from . import meta


# Try to import the official MCP SDK types if available
# This allows users to use the canonical types without us taking a hard dependency
_MCP_SDK_AVAILABLE = False
_mcp_types = None


# MCP-specific context object
class MCPToolContext(typing.Dict[str, typing.Any]):
    """Injected context object for MCP tool triggers."""

    pass


def _is_mcp_sdk_type(obj: Any) -> bool:
    """Check if an object is from the official MCP SDK.

    This uses module checking to detect any MCP SDK type,
    avoiding the need to hard-code specific type names.
    """
    global _MCP_SDK_AVAILABLE, _mcp_types
    if not _MCP_SDK_AVAILABLE or _mcp_types is None:
        try:
            from mcp import types as _mcp_types
            _MCP_SDK_AVAILABLE = True
        except ImportError:
            _mcp_types = None
            return False

    return _is_mcp_sdk_type_annotation(type(obj))


def _is_mcp_sdk_type_annotation(annotation: Any) -> bool:
    """Check if a return annotation is an official MCP SDK type.

    MCP SDK 1.x types are defined in ``mcp.types``. MCP SDK 2.x re-exports
    types defined in ``mcp_types`` from that same public module.
    """
    if isinstance(annotation, type):
        module = getattr(annotation, '__module__', None)
        if module and module.startswith('mcp.types'):
            return True

        if module and (module == 'mcp_types'
                       or module.startswith('mcp_types.')):
            global _MCP_SDK_AVAILABLE, _mcp_types
            if not _MCP_SDK_AVAILABLE or _mcp_types is None:
                try:
                    from mcp import types as _mcp_types
                    _MCP_SDK_AVAILABLE = True
                except ImportError:
                    _mcp_types = None
                    return False

            return any(exported is annotation
                       for exported in vars(_mcp_types).values())

        return False

    origin = typing.get_origin(annotation)
    if origin in (list, typing.Union):
        return any(arg is not type(None)
                   and _is_mcp_sdk_type_annotation(arg)
                   for arg in typing.get_args(annotation))

    return False


def _is_mcp_call_tool_result(obj: Any) -> bool:
    """Check if an object is CallToolResult from the official MCP SDK."""
    global _MCP_SDK_AVAILABLE, _mcp_types
    if not _MCP_SDK_AVAILABLE or _mcp_types is None:
        try:
            from mcp import types as _mcp_types
            _MCP_SDK_AVAILABLE = True
        except ImportError:
            _mcp_types = None
            return False

    # Check for CallToolResult from mcp.types
    if hasattr(_mcp_types, 'CallToolResult'):
        return isinstance(obj, _mcp_types.CallToolResult)

    return False


def _serialize_content_block(block: Any) -> dict:
    """Serialize a content block to a dictionary.

    Handles official mcp.types and @mcp_content decorated classes.
    """
    # If it's from the official MCP SDK
    if _is_mcp_sdk_type(block):
        # MCP SDK types should be JSON-serializable
        if hasattr(block, 'model_dump'):
            return block.model_dump(
                mode='json', exclude_none=True, by_alias=True)
        elif hasattr(block, 'dict'):
            return block.dict(exclude_none=True, by_alias=True)

    # If it's a dataclass (e.g., @mcp_content decorated)
    if is_dataclass(block) and not isinstance(block, type):
        return asdict(block)

    # If it's already a dict
    if isinstance(block, dict):
        return block

    # Fallback: try to convert to dict
    if hasattr(block, '__dict__'):
        return block.__dict__

    msg = f"Unable to serialize content block of type {type(block).__name__}"
    raise TypeError(msg)


class PromptInvocationContext:
    """Context object for MCP prompt triggers.

    Provides structured access to prompt invocation details including
    the prompt name, arguments, session information, and transport metadata.

    Attributes:
        name: The name of the prompt being invoked
        arguments: Dictionary of argument name to value (all values are strings)
        sessionid: Optional session ID for the invocation
        transport: Optional transport information dictionary

    Example:
        >>> context = PromptInvocationContext(data)
        >>> code = context.arguments.get("code", "")
        >>> language = context.arguments.get("language", "python")
    """

    def __init__(self, data: typing.Union[dict, str]):
        """Initialize from trigger data received from the host.

        Args:
            data: Either a dict containing the context or a JSON string
        """
        if isinstance(data, str):
            import json
            data = json.loads(data)

        self._data = data if isinstance(data, dict) else {}

    @property
    def name(self) -> str:
        """The name of the prompt being invoked."""
        return self._data.get('name', '')

    @property
    def arguments(self) -> typing.Dict[str, str]:
        """Dictionary of prompt arguments (all values are strings)."""
        return self._data.get('arguments', {})

    @property
    def sessionid(self) -> typing.Optional[str]:
        """Optional session ID for the invocation."""
        return self._data.get('sessionid')

    @property
    def transport(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Optional transport information."""
        return self._data.get('transport')

    def __repr__(self) -> str:
        return f"PromptInvocationContext(name={self.name!r}, arguments={self.arguments!r})"


class _MCPToolTriggerConverter(meta.InConverter, binding='mcpToolTrigger',
                               trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, dict, bytes, MCPToolContext))

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata):
        """Decode incoming MCP tool request data.

        Returns the raw data in its native format (string, dict, bytes).
        """
        # Handle different data types appropriately
        if data.type == 'json':
            # If it's already parsed JSON, use the value directly
            return data.value
        elif data.type == 'string':
            # If it's a string, use it as-is
            return data.value
        elif data.type == 'bytes':
            return data.value
        else:
            # Fallback to python_value for other types
            return data.python_value if hasattr(data, 'python_value') else data.value

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type] = None):
        """Encode the return value from MCP tool functions.

        Supports multiple return types:
        - Strings, bytes
        - Official mcp.types content blocks (TextContent, ImageContent, etc.)
        - Official mcp.types.CallToolResult
        - Classes decorated with @mcp_content
        """
        if obj is None:
            return meta.Datum(type='string', value='')
        elif isinstance(obj, str):
            return meta.Datum(type='string', value=obj)
        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))

        # Handle official MCP SDK CallToolResult
        elif _is_mcp_call_tool_result(obj):
            # Serialize the MCP SDK's CallToolResult
            if hasattr(obj, 'model_dump'):
                result_dict = obj.model_dump(
                    mode='json', exclude_none=True, by_alias=True)
            elif hasattr(obj, 'dict'):
                result_dict = obj.dict(exclude_none=True, by_alias=True)
            else:
                # Fallback: try to access attributes directly
                content_blocks = [_serialize_content_block(block)
                                  for block in obj.content]
                result_dict = {
                    'content': content_blocks if hasattr(obj, 'content') else [],
                }
                structured_content = getattr(
                    obj, 'structuredContent',
                    getattr(obj, 'structured_content', None))
                if structured_content is not None:
                    result_dict['structuredContent'] = structured_content
            result_json = json.dumps(result_dict)
            return meta.Datum(type='string', value=result_json)

        # Handle official MCP SDK content types
        elif _is_mcp_sdk_type(obj):
            serialized = _serialize_content_block(obj)
            return meta.Datum(type='string', value=json.dumps(serialized))

        # Handle list of MCP SDK content blocks
        elif isinstance(obj, list) and len(obj) > 0:
            # Check if it's a list of MCP SDK content blocks
            first_item = obj[0]
            if _is_mcp_sdk_type(first_item):
                blocks_list = [_serialize_content_block(block)
                               for block in obj]
                return meta.Datum(type='string', value=json.dumps(blocks_list))

        # Fallback: convert other types to string
        return meta.Datum(type='string', value=str(obj))


class MCPResourceTriggerConverter(meta.InConverter, binding='mcpResourceTrigger',
                                  trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, dict, bytes))

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata):
        """
        Decode incoming MCP resource request data.
        Returns the raw data in its native format (string, dict, bytes).
        """
        # Handle different data types appropriately
        if data.type == 'json':
            # If it's already parsed JSON, use the value directly
            return data.value
        elif data.type == 'string':
            # If it's a string, use it as-is
            return data.value
        elif data.type == 'bytes':
            return data.value
        else:
            # Fallback to python_value for other types
            return data.python_value if hasattr(data, 'python_value') else data.value

    @classmethod
    def encode(cls, obj: typing.Any, *, expected_type: typing.Optional[type] = None):
        """
        Encode the return value from MCP resource functions.
        MCP resources typically return string responses.
        """
        if obj is None:
            return meta.Datum(type='string', value='')
        elif isinstance(obj, str):
            return meta.Datum(type='string', value=obj)
        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))
        else:
            # Convert other types to string
            return meta.Datum(type='string', value=str(obj))


class _MCPPromptTriggerConverter(meta.InConverter, binding='mcpPromptTrigger',
                                 trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, dict, bytes, PromptInvocationContext))

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata):
        """
        Decode incoming MCP prompt request data.
        Returns a PromptInvocationContext object.
        """
        # Handle different data types appropriately
        if data.type == 'json':
            # If it's already parsed JSON, create context from dict
            return PromptInvocationContext(data.value)
        elif data.type == 'string':
            # If it's a JSON string, create context from string
            return PromptInvocationContext(data.value)
        elif data.type == 'bytes':
            # Decode bytes to string then create context
            return PromptInvocationContext(data.value.decode('utf-8'))
        else:
            # Fallback to python_value for other types
            value = data.python_value if hasattr(data, 'python_value') else data.value
            return PromptInvocationContext(value)

    @classmethod
    def encode(cls, obj: typing.Any, *, expected_type: typing.Optional[type] = None):
        """
        Encode the return value from MCP prompt functions.
        MCP prompts typically return string responses that the host wraps as messages.
        Can also return a JSON-serialized GetPromptResult for advanced scenarios.
        """
        if obj is None:
            return meta.Datum(type='string', value='')
        elif isinstance(obj, str):
            return meta.Datum(type='string', value=obj)
        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))
        else:
            # Convert other types to string
            return meta.Datum(type='string', value=str(obj))
