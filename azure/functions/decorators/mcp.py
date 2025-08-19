from typing import Optional

from azure.functions.decorators.constants import (
    MCP_TOOL_TRIGGER, MCP_TOOL_INPUT, MCP_TOOL_OUTPUT
)
from azure.functions.decorators.core import Trigger, DataType, InputBinding, \
    OutputBinding


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


class MCPToolInput(InputBinding):
  
    @staticmethod
    def get_binding_name() -> str:
        return MCP_TOOL_INPUT

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


class MCPToolOutput(OutputBinding):
   
    @staticmethod
    def get_binding_name() -> str:
        return MCP_TOOL_OUTPUT

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
