# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import inspect

from typing import List, Optional, Union, get_origin, get_args
from datetime import datetime

from azure.functions.decorators.constants import (
    MCP_TOOL_TRIGGER
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


class MCPToolTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return MCP_TOOL_TRIGGER

    def __init__(self,
                 name: str,
                 tool_name: str,
                 description: Optional[str] = None,
                 tool_properties: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.tool_name = tool_name
        self.description = description
        self.tool_properties = tool_properties
        super().__init__(name=name, data_type=data_type)


def unwrap_optional(pytype: type):
    """If Optional[T], return T; else return pytype unchanged."""
    origin = get_origin(pytype)
    args = get_args(pytype)
    if origin is Union and any(a is type(None) for a in args):
        non_none_args = [a for a in args if a is not type(None)]
        return non_none_args[0] if non_none_args else str
    return pytype


def check_is_array(param_type_hint: type) -> bool:
    """Return True if type is (possibly optional) list[...]"""
    unwrapped = unwrap_optional(param_type_hint)
    origin = get_origin(unwrapped)
    return origin in (list, List)


def check_property_type(pytype: type, is_array: bool) -> str:
    """Map Python type hints to MCP property types."""
    if isinstance(pytype, McpPropertyType):
        return pytype.value
    base_type = unwrap_optional(pytype)
    if is_array:
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
    if origin is Union and any(a is type(None) for a in args):
        return False

    # 3) It's required
    return True
