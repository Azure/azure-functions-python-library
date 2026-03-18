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
    type: str = field(default="resource", init=False)

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
