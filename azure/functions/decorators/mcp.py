# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import inspect
from dataclasses import dataclass
from typing import Any, List, Optional, Union, get_origin, get_args
from datetime import datetime

from ..mcp import MCPToolContext
from azure.functions.decorators.constants import (
    MCP_TOOL_TRIGGER, MCP_RESOURCE_TRIGGER, MCP_PROMPT_TRIGGER
)
from azure.functions.decorators.core import Trigger, DataType, McpPropertyType

# Mapping Python types to MCP property types
_TYPE_MAPPING = {
    int: "integer",
    float: "number",
    str: "string",
    bool: "boolean",
    object: "object",
    datetime: "string"
}


@dataclass
class PromptArgument:
    """Defines a prompt argument with its metadata.

    Args:
        name: The argument name
        description: Optional description of the argument
        required: Whether the argument is required (default: False)
    """

    name: str
    description: Optional[str] = None
    required: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary format expected by host."""
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required
        }

    def serializer(obj):
        if isinstance(obj, PromptArgument):
            return obj.to_dict()


class MCPResourceTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return MCP_RESOURCE_TRIGGER

    def __init__(self,
                 name: str,
                 uri: str,
                 resource_name: str,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 mime_type: Optional[str] = None,
                 size: Optional[int] = None,
                 metadata: Optional[str] = None,
                 use_result_schema: Optional[bool] = False,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.uri = uri
        self.resourceName = resource_name
        self.title = title
        self.description = description
        self.mimeType = mime_type
        self.size = size
        self.metadata = metadata
        self.useResultSchema = use_result_schema
        super().__init__(name=name, data_type=data_type)


class MCPPromptTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return MCP_PROMPT_TRIGGER

    def __init__(self,
                 name: str,
                 prompt_name: str,
                 prompt_arguments: Optional[str] = None,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 metadata: Optional[str] = None,
                 icons: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.promptName = prompt_name
        self.title = title
        self.description = description
        self.metadata = metadata
        self.icons = icons
        self.promptArguments = prompt_arguments

        super().__init__(name=name, data_type=data_type)


class _MCPToolTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return MCP_TOOL_TRIGGER

    def __init__(self,
                 name: str,
                 tool_name: str,
                 description: Optional[str] = None,
                 tool_properties: Optional[str] = None,
                 metadata: Optional[str] = None,
                 use_result_schema: Optional[bool] = False,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.tool_name = tool_name
        self.description = description
        self.tool_properties = tool_properties
        self.metadata = metadata
        self.use_result_schema = use_result_schema
        super().__init__(name=name, data_type=data_type)


def unwrap_optional(pytype: type):
    """If Optional[T], return T; else return pytype unchanged."""
    origin = get_origin(pytype)
    args = get_args(pytype)
    if origin is Union and any(a is type(None) for a in args):  # noqa
        non_none_args = [a for a in args if a is not type(None)]  # noqa
        return non_none_args[0] if non_none_args else str
    return pytype


def check_as_array(param_type_hint: type) -> bool:
    """Return True if type is (possibly optional) list[...]"""
    unwrapped = unwrap_optional(param_type_hint)
    origin = get_origin(unwrapped)
    return origin in (list, List)


def check_property_type(pytype: type, as_array: bool) -> str:
    """Map Python type hints to MCP property types."""
    if isinstance(pytype, McpPropertyType):
        return pytype.value
    base_type = unwrap_optional(pytype)
    if as_array:
        args = get_args(base_type)
        inner_type = unwrap_optional(args[0]) if args else str
        return _TYPE_MAPPING.get(inner_type, "string")
    return _TYPE_MAPPING.get(base_type, "string")


def check_is_required(param: type, param_type_hint: type) -> bool:
    """
    Return True when param is required, False when optional.

    Rules:
    - If param has an explicit default -> not required
    - If annotation is Optional[T] (Union[..., None]) -> not required
    - Otherwise -> required
    """
    # 1) default value present => not required
    if param.default is not inspect.Parameter.empty:
        return False

    # 2) Optional[T] => not required
    origin = get_origin(param_type_hint)
    args = get_args(param_type_hint)
    if origin is Union and any(a is type(None) for a in args):  # noqa
        return False

    # 3) It's required
    return True


def build_property_metadata(sig,
                            skip_param_names: List[str],
                            explicit_properties: dict) -> List[dict]:
    """Build the tool_properties list for MCPToolTrigger based on function signature."""
    tool_properties = []
    for param_name, param in sig.parameters.items():
        if param_name in skip_param_names:
            continue
        param_type_hint = param.annotation if param.annotation != inspect.Parameter.empty else str  # noqa

        if param_type_hint is MCPToolContext:
            continue

        # Inferred defaults
        is_required = check_is_required(param, param_type_hint)
        as_array = check_as_array(param_type_hint)
        property_type = check_property_type(param_type_hint, as_array)

        property_data = {
            "propertyName": param_name,
            "propertyType": property_type,
            "description": "",
            "isArray": as_array,
            "isRequired": is_required
        }

        # Merge in any explicit overrides
        if param_name in explicit_properties:
            overrides = explicit_properties[param_name]
            for key, value in overrides.items():
                if value is not None:
                    property_data[key] = value

        tool_properties.append(property_data)
    return tool_properties


def has_mcp_content_marker(obj: Any) -> bool:
    """
    Check if an object or its type is marked for structured content generation.
    Returns True if the object's class has '__mcp_content__' attribute set to True.
    Handles both class types and instances.
    """
    if obj is None:
        return False

    # If obj is already a class type, check it directly
    if isinstance(obj, type):
        return getattr(obj, '__mcp_content__', False) is True

    # Otherwise, get the type and check
    obj_type = type(obj)
    return getattr(obj_type, '__mcp_content__', False) is True


def should_create_structured_content(obj: Any) -> bool:
    """
    Determines whether structured content should be created for the given object.

    Returns True if:
    - The object's class is decorated with a marker that sets __mcp_content__ = True
    - The object is not a primitive type (str, int, float, bool, None)
    - The object is not a dict or list

    This mimics the .NET implementation's McpContentAttribute checking.
    """
    if obj is None:
        return False

    # Primitive types don't generate structured content unless explicitly marked
    if isinstance(obj, (str, int, float, bool, dict, list)):
        return False

    # Check for the marker attribute
    return has_mcp_content_marker(obj)


def mcp_content(cls):
    """
    Decorator to mark a class as an MCP result type that should be serialized
    as structured content.

    When a function returns an object of a type decorated with this decorator,
    the result will be serialized as both text content (for backwards compatibility)
    and structured content (for clients that support it).

    This is the Python equivalent of C#'s [McpContent] attribute.

    Example:
        @mcp_content
        class ImageMetadata:
            def __init__(self, image_id: str, format: str, tags: list):
                self.image_id = image_id
                self.format = format
                self.tags = tags

        @app.mcp_tool(use_result_schema=True)
        def get_image_info():
            return ImageMetadata("logo", "png", ["functions"])
    """
    cls.__mcp_content__ = True
    return cls
