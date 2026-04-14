# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import typing

from . import meta


# MCP-specific context object
class MCPToolContext(typing.Dict[str, typing.Any]):
    """Injected context object for MCP tool triggers."""

    pass


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
        """
        Decode incoming MCP tool request data.
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
        Encode the return value from MCP tool functions.
        MCP tools typically return string responses.
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
