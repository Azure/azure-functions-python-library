#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import typing
import unittest

import azure.functions as func
from azure.functions import DataType, MCPToolContext
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.mcp import MCPToolTrigger
from azure.functions.mcp import MCPToolTriggerConverter
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

    def test_trigger_converter(self):
        # Test with string data
        datum = Datum(value='{"arguments":{}}', type='string')
        result = MCPToolTriggerConverter.decode(datum, trigger_metadata={})
        self.assertEqual(result, '{"arguments":{}}')
        self.assertIsInstance(result, str)

        # Test with json data
        datum_json = Datum(value={"arguments": {}}, type='json')
        result_json = MCPToolTriggerConverter.decode(datum_json, trigger_metadata={})
        self.assertEqual(result_json, {"arguments": {}})
        self.assertIsInstance(result_json, dict)


class TestMcpToolDecorator(unittest.TestCase):
    def setUp(self):
        self.app = func.FunctionApp()

    def tearDown(self):
        self.app = None

    def test_simple_signature(self):
        @self.app.mcp_tool()
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "The a parameter."}, '
                         '{"propertyName": "b", "propertyType": "integer", '
                         '"description": "The b parameter."}]')

    def test_with_binding_argument(self):
        @self.app.mcp_tool()
        def save_snippet(file, snippetname: str, snippet: str):
            """Save snippet."""
            return f"Saved {snippetname}"

        trigger = save_snippet._function._bindings[0]
        self.assertEqual(trigger.description, "Save snippet.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "save_snippet")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "file", '
                         '"propertyType": "string", '
                         '"description": "The file parameter."}, '
                         '{"propertyName": "snippetname", '
                         '"propertyType": "string", '
                         '"description": "The snippetname parameter."}, '
                         '{"propertyName": "snippet", '
                         '"propertyType": "string", '
                         '"description": "The snippet parameter."}]')

    def test_with_context_argument(self):
        @self.app.mcp_tool()
        def process_data(data: str, context: MCPToolContext):
            """Process data with context."""
            return f"Processed {data}"

        trigger = process_data._function._bindings[0]
        self.assertEqual(trigger.description, "Process data with context.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "process_data")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "data", '
                         '"propertyType": "string", '
                         '"description": "The data parameter."}]')

    def test_with_annotated(self):
        @self.app.mcp_tool()
        def add_numbers(
                a: typing.Annotated[int, "First number"],
                b: typing.Annotated[int, "Second number"]
        ) -> str:
            """Add two integers."""
            return str(a + b)

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two integers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "First number"}, '
                         '{"propertyName": "b", '
                         '"propertyType": "integer", '
                         '"description": "Second number"}]')
