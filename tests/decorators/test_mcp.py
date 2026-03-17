#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import typing
import unittest

import azure.functions as func
from azure.functions import DataType, MCPToolContext
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.mcp import _MCPToolTrigger, MCPResourceTrigger
from azure.functions.mcp import _MCPToolTriggerConverter, MCPResourceTriggerConverter
from azure.functions.meta import Datum


class TestMCP(unittest.TestCase):
    def test_mcp_tool_trigger_valid_creation(self):
        trigger = _MCPToolTrigger(
            name="context",
            tool_name="hello",
            description="Hello world.",
            tool_properties="[]",
            metadata='{"key": "value"}',
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
                "metadata": '{"key": "value"}',
                "direction": BindingDirection.IN,
            },
        )

    def test_trigger_converter(self):
        # Test with string data
        datum = Datum(value='{"arguments":{}}', type='string')
        result = _MCPToolTriggerConverter.decode(datum, trigger_metadata={})
        self.assertEqual(result, '{"arguments":{}}')
        self.assertIsInstance(result, str)

        # Test with json data
        datum_json = Datum(value={"arguments": {}}, type='json')
        result_json = _MCPToolTriggerConverter.decode(datum_json, trigger_metadata={})
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

    def test_simple_signature_defaults_metadata(self):
        @self.app.mcp_tool(metadata='{"key": "value"}')
        def add_numbers(a, b):
            return a + b

        trigger = add_numbers._function._bindings[0]
        self.assertEqual(trigger.description, "")
        self.assertEqual(trigger.name, "context")
        self.assertEqual(trigger.tool_name, "add_numbers")
        self.assertEqual(trigger.metadata, '{"key": "value"}')
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


class TestMCPResourceTrigger(unittest.TestCase):
    def test_mcp_resource_trigger_valid_creation(self):
        trigger = MCPResourceTrigger(
            name="context",
            uri="file://readme.md",
            resource_name="myresource",
            title="my title",
            description="my resource description",
            mime_type="Text/Markdown",
            size=1024,
            metadata="",
            data_type=DataType.UNDEFINED,
            dummy_field="dummy",
        )
        self.assertEqual(trigger.get_binding_name(), "mcpResourceTrigger")
        self.assertEqual(
            trigger.get_dict_repr(),
            {
                "name": "context",
                "uri": "file://readme.md",
                "resourceName": "myresource",
                "title": "my title",
                "description": "my resource description",
                "mimeType": "Text/Markdown",
                "size": 1024,
                "metadata": "",
                "type": "mcpResourceTrigger",
                "dataType": DataType.UNDEFINED,
                "dummyField": "dummy",
                "direction": BindingDirection.IN,
            },
        )

    def test_mcp_resource_trigger_only_required_args_creation(self):
        trigger = MCPResourceTrigger(
            name="context",
            uri="file://readme.md",
            resource_name="myresource"
        )
        self.assertEqual(trigger.get_binding_name(), "mcpResourceTrigger")
        self.assertEqual(
            trigger.get_dict_repr(),
            {
                "name": "context",
                "uri": "file://readme.md",
                "resourceName": "myresource",
                "type": "mcpResourceTrigger",
                "direction": BindingDirection.IN,
            },
        )

    def test_trigger_converter(self):
        # Test with string data
        datum = Datum(value='{"arguments":{}}', type='string')
        result = MCPResourceTriggerConverter.decode(datum, trigger_metadata={})
        self.assertEqual(result, '{"arguments":{}}')
        self.assertIsInstance(result, str)

        # Test with json data
        datum_json = Datum(value={"arguments": {}}, type='json')
        result_json = MCPResourceTriggerConverter.decode(datum_json, trigger_metadata={})
        self.assertEqual(result_json, {"arguments": {}})
        self.assertIsInstance(result_json, dict)


class TestStructuredContent(unittest.TestCase):
    """Tests for structured content functionality"""

    def setUp(self):
        self.app = func.FunctionApp()

    def tearDown(self):
        self.app = None

    def test_mcp_content_decorator(self):
        """Test that @mcp_content decorator marks a class properly"""
        from azure.functions.decorators.mcp import has_mcp_content_marker
        
        @func.mcp_content
        class TestData:
            def __init__(self, value: str):
                self.value = value
        
        instance = TestData("test")
        self.assertTrue(has_mcp_content_marker(instance))
        self.assertTrue(hasattr(TestData, '__mcp_content__'))
        self.assertEqual(TestData.__mcp_content__, True)

    def test_should_create_structured_content_for_marked_class(self):
        """Test that marked classes generate structured content"""
        from azure.functions.decorators.mcp import should_create_structured_content
        
        @func.mcp_content
        class MarkedData:
            def __init__(self, name: str):
                self.name = name
        
        instance = MarkedData("test")
        self.assertTrue(should_create_structured_content(instance))

    def test_should_not_create_structured_content_for_primitives(self):
        """Test that primitive types don't generate structured content"""
        from azure.functions.decorators.mcp import should_create_structured_content
        
        self.assertFalse(should_create_structured_content("string"))
        self.assertFalse(should_create_structured_content(42))
        self.assertFalse(should_create_structured_content(3.14))
        self.assertFalse(should_create_structured_content(True))
        self.assertFalse(should_create_structured_content(None))

    def test_should_not_create_structured_content_for_unmarked_class(self):
        """Test that unmarked classes don't generate structured content"""
        from azure.functions.decorators.mcp import should_create_structured_content
        
        class UnmarkedData:
            def __init__(self, value: str):
                self.value = value
        
        instance = UnmarkedData("test")
        self.assertFalse(should_create_structured_content(instance))

    def test_mcp_tool_with_use_result_schema_parameter(self):
        """Test that use_result_schema parameter is passed to trigger"""
        @self.app.mcp_tool(use_result_schema=True)
        def test_tool(value: str):
            """Test tool with result schema"""
            return value
        
        trigger = test_tool._function._bindings[0]
        self.assertEqual(trigger.useResultSchema, True)
        self.assertEqual(trigger.tool_name, "test_tool")

    def test_mcp_content_with_dataclass(self):
        """Test mcp_content decorator works with dataclasses"""
        from dataclasses import dataclass
        from azure.functions.decorators.mcp import should_create_structured_content
        
        @func.mcp_content
        @dataclass
        class DataModel:
            name: str
            count: int
        
        instance = DataModel(name="test", count=5)
        self.assertTrue(should_create_structured_content(instance))
        self.assertTrue(hasattr(DataModel, '__mcp_content__'))


class TestContentBlocks(unittest.TestCase):
    """Tests for ContentBlock types"""

    def test_text_content_block_creation(self):
        """Test creating a TextContentBlock"""
        block = func.TextContentBlock(text="Hello, world!")
        self.assertEqual(block.type, "text")
        self.assertEqual(block.text, "Hello, world!")
        self.assertEqual(block.to_dict(), {"type": "text", "text": "Hello, world!"})

    def test_image_content_block_creation(self):
        """Test creating an ImageContentBlock"""
        block = func.ImageContentBlock(data="base64data", mime_type="image/png")
        self.assertEqual(block.type, "image")
        self.assertEqual(block.data, "base64data")
        self.assertEqual(block.mime_type, "image/png")
        
        block_dict = block.to_dict()
        self.assertEqual(block_dict["type"], "image")
        self.assertEqual(block_dict["data"], "base64data")
        self.assertEqual(block_dict["mimeType"], "image/png")

    def test_resource_link_block_creation(self):
        """Test creating a ResourceLinkBlock"""
        block = func.ResourceLinkBlock(
            uri="https://example.com/resource",
            name="Example Resource",
            description="A test resource",
            mime_type="application/json"
        )
        self.assertEqual(block.type, "resource")
        self.assertEqual(block.uri, "https://example.com/resource")
        self.assertEqual(block.name, "Example Resource")
        
        block_dict = block.to_dict()
        self.assertEqual(block_dict["type"], "resource")
        self.assertEqual(block_dict["uri"], "https://example.com/resource")
        self.assertEqual(block_dict["mimeType"], "application/json")

    def test_resource_link_block_minimal(self):
        """Test ResourceLinkBlock with only required fields"""
        block = func.ResourceLinkBlock(uri="file://logo.png")
        self.assertEqual(block.type, "resource")
        self.assertEqual(block.uri, "file://logo.png")
        
        block_dict = block.to_dict()
        self.assertEqual(block_dict["type"], "resource")
        self.assertEqual(block_dict["uri"], "file://logo.png")
        self.assertNotIn("name", block_dict)
        self.assertNotIn("description", block_dict)

    def test_call_tool_result_creation(self):
        """Test creating a CallToolResult"""
        result = func.CallToolResult(
            content=[
                func.TextContentBlock(text="Here's the data"),
                func.ImageContentBlock(data="imagedata", mime_type="image/jpeg")
            ],
            structured_content={"key": "value", "count": 42}
        )
        
        self.assertEqual(len(result.content), 2)
        self.assertIsInstance(result.content[0], func.TextContentBlock)
        self.assertIsInstance(result.content[1], func.ImageContentBlock)
        self.assertEqual(result.structured_content, {"key": "value", "count": 42})
        
        result_dict = result.to_dict()
        self.assertIn("content", result_dict)
        self.assertIn("structuredContent", result_dict)
        self.assertEqual(len(result_dict["content"]), 2)

    def test_call_tool_result_without_structured_content(self):
        """Test CallToolResult without structured content"""
        result = func.CallToolResult(
            content=[func.TextContentBlock(text="Simple text")]
        )
        
        self.assertIsNone(result.structured_content)
        result_dict = result.to_dict()
        self.assertIn("content", result_dict)
        self.assertEqual(result.structured_content, None)


