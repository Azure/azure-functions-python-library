# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Optional
from datetime import datetime

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
