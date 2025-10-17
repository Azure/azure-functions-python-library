from typing import Optional
from typing import Any, Dict, Tuple, get_args, get_origin, Annotated
import logging

from azure.functions.decorators.constants import (
    MCP_TOOL_TRIGGER
)
from azure.functions.decorators.core import Trigger, DataType
from azure.functions.decorators.function_app import FunctionBuilder

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

# MCP-specific context object
class MCPToolContext(Dict[str, Any]):
    """Injected context object for MCP tool triggers."""
    pass

# Helper to extract actual type and description from Annotated types
def _extract_type_and_description(param_name: str, type_hint: Any) -> Tuple[Any, str]:
    if get_origin(type_hint) is Annotated:
        args = get_args(type_hint)
        actual_type = args[0]
        # Use first string annotation as description if present
        param_description = next((a for a in args[1:] if isinstance(a, str)), f"The {param_name} parameter.")
        return actual_type, param_description
    return type_hint, f"The {param_name} parameter."

def _get_user_function(target_func):
    """
    Unwraps decorated or builder-wrapped functions to find the original
    user-defined function (the one starting with 'def' or 'async def').
    """
    logging.info("HELLO FROM THE SDK")
    # Case 1: It's a FunctionBuilder object
    if isinstance(target_func, FunctionBuilder):
        # Access the internal user function
        try:
            return target_func._function.get_user_function()
        except AttributeError:
            pass

    # Case 2: It's already the user-defined function
    if callable(target_func) and hasattr(target_func, "__name__"):
        return target_func

    # Case 3: It might be a partially wrapped callable
    if hasattr(target_func, "__wrapped__"):
        return _get_user_function(target_func.__wrapped__)

    # Default fallback
    return target_func
