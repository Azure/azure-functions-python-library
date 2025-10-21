from typing import Optional
from typing import Any, Dict, Tuple, get_args, get_origin, Annotated
import logging

from azure.functions.decorators.constants import (
    MCP_TOOL_TRIGGER
)
from azure.functions.decorators.core import Trigger, DataType

# Mapping Python types to MCP property types
_TYPE_MAPPING = {
    int: "integer",
    float: "number",
    str: "string",
    bool: "boolean",
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


# Helper to extract actual type and description from Annotated types
def _extract_type_and_description(param_name: str, type_hint: Any) -> Tuple[Any, str]:
    if get_origin(type_hint) is Annotated:
        args = get_args(type_hint)
        actual_type = args[0]
        # Use first string annotation as description if present
        param_description = next((a for a in args[1:] if isinstance(a, str)), f"The {param_name} parameter.")
        return actual_type, param_description
    return type_hint, f"The {param_name} parameter."
