# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import typing
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any

from . import meta


# MCP-specific context object
class MCPToolContext(typing.Dict[str, typing.Any]):
    """Injected context object for MCP tool triggers."""

    pass


# ContentBlock types for MCP responses
@dataclass
class ContentBlock:
    """Base class for MCP content blocks."""
    type: str = field(init=False)

    def to_dict(self) -> dict:
        """Convert the content block to a dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class TextContentBlock(ContentBlock):
    """Text content block for MCP responses."""
    text: str
    type: str = field(default="text", init=False)


@dataclass
class ImageContentBlock(ContentBlock):
    """Image content block for MCP responses."""
    data: str  # base64-encoded image data
    mime_type: str
    type: str = field(default="image", init=False)

    def to_dict(self) -> dict:
        """Convert to dict with correct JSON property names."""
        return {
            "type": self.type,
            "data": self.data,
            "mimeType": self.mime_type
        }


@dataclass
class ResourceLinkBlock(ContentBlock):
    """Resource link content block for MCP responses."""
    uri: str
    name: Optional[str] = None
    description: Optional[str] = None
    mime_type: Optional[str] = None
    type: str = field(default="resource_link", init=False)

    def to_dict(self) -> dict:
        """Convert to dict with correct JSON property names."""
        result = {
            "type": self.type,
            "uri": self.uri
        }
        if self.name is not None:
            result["name"] = self.name
        if self.description is not None:
            result["description"] = self.description
        if self.mime_type is not None:
            result["mimeType"] = self.mime_type
        return result


@dataclass
class CallToolResult:
    """
    Result type for MCP tool calls that allows manual construction
    of content blocks and structured content.

    Example:
        return CallToolResult(
            content=[
                TextContentBlock(text="Here's the data"),
                ImageContentBlock(data=base64_data, mime_type="image/png")
            ],
            structured_content={"key": "value"}
        )
    """
    content: List[ContentBlock]
    structured_content: Optional[Any] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "content": [block.to_dict() for block in self.content]
        }
        if self.structured_content is not None:
            result["structuredContent"] = self.structured_content
        return result


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
