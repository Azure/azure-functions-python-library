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
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}, '
                         '{"propertyName": "b", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_long_pydocs(self):
        @self.app.mcp_tool()
        def add_numbers(a: int, b: int) -> int:
            """
            Add two numbers.

            Args:
                a (int): The first number to add.
                b (int): The second number to add.

            Returns:
                int: The sum of the two numbers.
            """
            return a + b

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, '''Add two numbers.

Args:
    a (int): The first number to add.
    b (int): The second number to add.

Returns:
    int: The sum of the two numbers.''')
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}, '
                         '{"propertyName": "b", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_simple_signature_defaults(self):
        @self.app.mcp_tool()
        def add_numbers(a, b):
            return a + b

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "string", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}, '
                         '{"propertyName": "b", '
                         '"propertyType": "string", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_with_binding_argument(self):
        @self.app.mcp_tool()
        @self.app.blob_input(arg_name="file", path="", connection="Test")
        def save_snippet(file, snippetname: str, snippet: str):
            """Save snippet."""
            return f"Saved {snippetname}"

        trigger = save_snippet._function._bindings[1]
        self.assertEqual(trigger.description, "Save snippet.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "save_snippet")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "snippetname", '
                         '"propertyType": "string", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}, '
                         '{"propertyName": "snippet", '
                         '"propertyType": "string", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

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
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_with_only_context(self):
        @self.app.mcp_tool()
        def process_data(context: MCPToolContext):
            """Process data with context."""
            return f"Processed {context}"

        trigger = process_data._function._bindings[0]
        self.assertEqual(trigger.description, "Process data with context.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "process_data")
        self.assertEqual(trigger.tool_properties,
                         '[]')

    def test_is_required(self):
        @self.app.mcp_tool()
        def add_numbers(a: typing.Optional[int] = 0) -> int:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": false}]')

    def test_is_required_default_value(self):
        @self.app.mcp_tool()
        def add_numbers(a: int = 0) -> int:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": false}]')

    def test_as_array(self):
        @self.app.mcp_tool()
        def add_numbers(a: typing.List[int]) -> typing.List[int]:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": true, '
                         '"isRequired": true}]')

    def test_as_array_pep(self):
        @self.app.mcp_tool()
        def add_numbers(a: list[int]) -> list[int]:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": true, '
                         '"isRequired": true}]')

    def test_is_optional_array(self):
        @self.app.mcp_tool()
        def add_numbers(a: typing.Optional[typing.List[int]]):
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": true, '
                         '"isRequired": false}]')

    def test_mcp_property_input_all_props(self):
        @self.app.mcp_tool()
        @self.app.mcp_tool_property(arg_name="a",
                                    description="The first number",
                                    property_type=func.McpPropertyType.INTEGER,
                                    is_required=False,
                                    as_array=True)
        def add_numbers(a, b: int) -> int:
            """Add two numbers."""
            return a + b

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "integer", '
                         '"description": "The first number", '
                         '"isArray": true, '
                         '"isRequired": false}, '
                         '{"propertyName": "b", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_mcp_property_input_one_prop(self):
        @self.app.mcp_tool()
        @self.app.mcp_tool_property(arg_name="a", description="The first number")
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
                         '"description": "The first number", '
                         '"isArray": false, '
                         '"isRequired": true}, '
                         '{"propertyName": "b", '
                         '"propertyType": "integer", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_mcp_property_input_enum_float(self):
        @self.app.mcp_tool()
        @self.app.mcp_tool_property(arg_name="a", property_type=func.McpPropertyType.FLOAT)
        def add_numbers(a) -> int:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "float", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_mcp_property_input_enum_string(self):
        @self.app.mcp_tool()
        @self.app.mcp_tool_property(arg_name="a", property_type=func.McpPropertyType.STRING)
        def add_numbers(a) -> int:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "string", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_mcp_property_input_enum_bool(self):
        @self.app.mcp_tool()
        @self.app.mcp_tool_property(arg_name="a", property_type=func.McpPropertyType.BOOLEAN)
        def add_numbers(a) -> int:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "boolean", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_mcp_property_input_enum_object(self):
        @self.app.mcp_tool()
        @self.app.mcp_tool_property(arg_name="a", property_type=func.McpPropertyType.OBJECT)
        def add_numbers(a) -> int:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "object", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')

    def test_mcp_property_input_enum_datetime(self):
        @self.app.mcp_tool()
        @self.app.mcp_tool_property(arg_name="a", property_type=func.McpPropertyType.DATETIME)
        def add_numbers(a) -> int:
            """Add two numbers."""
            return a

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "Add two numbers.")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.tool_properties,
                         '[{"propertyName": "a", '
                         '"propertyType": "string", '
                         '"description": "", '
                         '"isArray": false, '
                         '"isRequired": true}]')
