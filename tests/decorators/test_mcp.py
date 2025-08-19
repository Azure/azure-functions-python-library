import unittest

from azure.functions import DataType
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.mcp import MCPToolTrigger, MCPToolInput, MCPToolOutput
from azure.functions.mcp import MCPToolRequest, MCPToolTriggerConverter, MCPToolOutputConverter
from azure.functions.meta import Datum


class TestMCP(unittest.TestCase):
    def test_mcp_tool_trigger_valid_creation(self):
        trigger = MCPToolTrigger(
            name="context",
            tool_name="hello",
            description="Hello world.",
            tool_properties="[]",
            data_type=DataType.UNDEFINED,
            dummy_field="dummy",
        )
        self.assertEqual(trigger.get_binding_name(), "mcpToolTrigger")
        self.assertEqual(
            trigger.get_dict_repr(),
            {
                "name": "context",
                "toolName": "hello",
                "description": "Hello world.",
                "toolProperties": "[]",
                "type": "mcpToolTrigger",
                "dataType": DataType.UNDEFINED,
                "dummyField": "dummy",
                "direction": BindingDirection.IN,
            },
        )

    def test_mcp_tool_input_valid_creation(self):
        ib = MCPToolInput(
            name="param",
            tool_name="hello",
            description="desc",
            tool_properties="[]",
            data_type=DataType.UNDEFINED,
            dummy_field="dummy",
        )
        self.assertEqual(ib.get_binding_name(), "mcpToolInput")
        d = ib.get_dict_repr()
        self.assertEqual(d["toolName"], "hello")
        self.assertEqual(d["direction"], BindingDirection.IN)

    def test_mcp_tool_output_valid_creation(self):
        ob = MCPToolOutput(
            name="out",
            tool_name="hello",
            description="desc",
            tool_properties="[]",
            data_type=DataType.UNDEFINED,
        )
        self.assertEqual(ob.get_binding_name(), "mcpToolOutput")
        d = ob.get_dict_repr()
        self.assertEqual(d["direction"], BindingDirection.OUT)

    def test_trigger_converter(self):
        # Test with string data
        datum = Datum(value='{"arguments":{}}', type='string')
        req = MCPToolTriggerConverter.decode(datum, trigger_metadata={})
        self.assertTrue(isinstance(req, MCPToolRequest))
        self.assertIsNotNone(req.json)
        
        # Test with json data 
        datum_json = Datum(value={"arguments": {}}, type='json')
        req_json = MCPToolTriggerConverter.decode(datum_json, trigger_metadata={})
        self.assertTrue(isinstance(req_json, MCPToolRequest))

    def test_output_converter(self):
        datum = MCPToolOutputConverter.encode("result", expected_type=str)
        self.assertEqual(datum.type, 'string')
        self.assertEqual(datum.value, 'result')
