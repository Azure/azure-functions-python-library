#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import typing
import unittest
import json

import azure.functions as func
from azure.functions import (DataType, MCPToolContext,
                             PromptInvocationContext, PromptArgument)
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.mcp import (_MCPToolTrigger,
                                            MCPResourceTrigger,
                                            MCPPromptTrigger)
from azure.functions.mcp import (_MCPToolTriggerConverter,
                                 MCPResourceTriggerConverter)
from azure.functions.meta import Datum


class TestMCP(unittest.TestCase):
    def test_mcp_tool_trigger_valid_creation(self):
        trigger = _MCPToolTrigger(
            name="context",
            tool_name="hello",
            description="Hello world.",
            tool_properties="[]",
            metadata='{"key": "value"}',
            use_result_schema=True,
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
                'useResultSchema': True,
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
        self.assertEqual(trigger.use_result_schema, True)
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
        self.assertEqual(block.type, "resource_link")
        self.assertEqual(block.uri, "https://example.com/resource")
        self.assertEqual(block.name, "Example Resource")

        block_dict = block.to_dict()
        self.assertEqual(block_dict["type"], "resource_link")
        self.assertEqual(block_dict["uri"], "https://example.com/resource")
        self.assertEqual(block_dict["mimeType"], "application/json")

    def test_resource_link_block_minimal(self):
        """Test ResourceLinkBlock with only required fields"""
        block = func.ResourceLinkBlock(uri="file://logo.png")
        self.assertEqual(block.type, "resource_link")
        self.assertEqual(block.uri, "file://logo.png")

        block_dict = block.to_dict()
        self.assertEqual(block_dict["type"], "resource_link")
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

    def test_text_content_block_empty_string(self):
        """Test TextContentBlock with empty string"""
        block = func.TextContentBlock(text="")
        self.assertEqual(block.text, "")
        self.assertEqual(block.to_dict(), {"type": "text", "text": ""})

    def test_text_content_block_multiline(self):
        """Test TextContentBlock with multiline text"""
        multiline_text = """Line 1
Line 2
Line 3"""
        block = func.TextContentBlock(text=multiline_text)
        self.assertEqual(block.text, multiline_text)
        block_dict = block.to_dict()
        self.assertIn("Line 1\nLine 2\nLine 3", block_dict["text"])

    def test_text_content_block_special_characters(self):
        """Test TextContentBlock with special characters"""
        special_text = 'Text with "quotes" and \'apostrophes\' and <tags>'
        block = func.TextContentBlock(text=special_text)
        self.assertEqual(block.text, special_text)
        block_dict = block.to_dict()
        self.assertEqual(block_dict["text"], special_text)

    def test_image_content_block_different_mime_types(self):
        """Test ImageContentBlock with various MIME types"""
        mime_types = ["image/png", "image/jpeg", "image/gif", "image/svg+xml"]
        for mime_type in mime_types:
            block = func.ImageContentBlock(data="data123", mime_type=mime_type)
            self.assertEqual(block.mime_type, mime_type)
            block_dict = block.to_dict()
            self.assertEqual(block_dict["mimeType"], mime_type)

    def test_image_content_block_property_naming(self):
        """Test that ImageContentBlock uses camelCase in JSON (mimeType not mime_type)"""
        block = func.ImageContentBlock(data="base64", mime_type="image/png")
        block_dict = block.to_dict()

        # Should use camelCase in JSON
        self.assertIn("mimeType", block_dict)
        self.assertNotIn("mime_type", block_dict)
        self.assertEqual(block_dict["mimeType"], "image/png")

    def test_image_content_block_large_data(self):
        """Test ImageContentBlock with large base64 data"""
        large_data = "A" * 10000  # Simulate large base64 string
        block = func.ImageContentBlock(data=large_data, mime_type="image/png")
        self.assertEqual(len(block.data), 10000)
        block_dict = block.to_dict()
        self.assertEqual(len(block_dict["data"]), 10000)

    def test_resource_link_block_all_fields(self):
        """Test ResourceLinkBlock with all fields populated"""
        block = func.ResourceLinkBlock(
            uri="https://example.com/api/resource",
            name="Test Resource",
            description="A detailed description",
            mime_type="application/json"
        )
        block_dict = block.to_dict()

        self.assertEqual(block_dict["type"], "resource_link")
        self.assertEqual(block_dict["uri"], "https://example.com/api/resource")
        self.assertEqual(block_dict["name"], "Test Resource")
        self.assertEqual(block_dict["description"], "A detailed description")
        self.assertEqual(block_dict["mimeType"], "application/json")

    def test_resource_link_block_partial_fields(self):
        """Test ResourceLinkBlock with some optional fields None"""
        block = func.ResourceLinkBlock(
            uri="file://path/to/file.txt",
            name="MyFile"
        )
        block_dict = block.to_dict()

        self.assertEqual(block_dict["uri"], "file://path/to/file.txt")
        self.assertEqual(block_dict["name"], "MyFile")
        self.assertNotIn("description", block_dict)
        self.assertNotIn("mimeType", block_dict)

    def test_resource_link_block_file_uri(self):
        """Test ResourceLinkBlock with file:// URI"""
        block = func.ResourceLinkBlock(uri="file://logo.png")
        self.assertEqual(block.uri, "file://logo.png")
        block_dict = block.to_dict()
        self.assertEqual(block_dict["uri"], "file://logo.png")

    def test_resource_link_block_http_uri(self):
        """Test ResourceLinkBlock with http:// and https:// URIs"""
        http_block = func.ResourceLinkBlock(uri="http://example.com")
        https_block = func.ResourceLinkBlock(uri="https://example.com")

        self.assertEqual(http_block.uri, "http://example.com")
        self.assertEqual(https_block.uri, "https://example.com")

    def test_call_tool_result_multiple_text_blocks(self):
        """Test CallToolResult with multiple TextContentBlocks"""
        result = func.CallToolResult(
            content=[
                func.TextContentBlock(text="First paragraph"),
                func.TextContentBlock(text="Second paragraph"),
                func.TextContentBlock(text="Third paragraph")
            ]
        )

        self.assertEqual(len(result.content), 3)
        result_dict = result.to_dict()
        self.assertEqual(len(result_dict["content"]), 3)
        self.assertEqual(result_dict["content"][0]["text"], "First paragraph")
        self.assertEqual(result_dict["content"][2]["text"], "Third paragraph")

    def test_call_tool_result_mixed_content_blocks(self):
        """Test CallToolResult with mixed ContentBlock types"""
        result = func.CallToolResult(
            content=[
                func.TextContentBlock(text="Description"),
                func.ResourceLinkBlock(uri="https://link.com", name="Link"),
                func.ImageContentBlock(data="img123", mime_type="image/png"),
                func.TextContentBlock(text="Footer")
            ]
        )

        self.assertEqual(len(result.content), 4)
        result_dict = result.to_dict()

        # Verify each block is correctly serialized
        self.assertEqual(result_dict["content"][0]["type"], "text")
        self.assertEqual(result_dict["content"][1]["type"], "resource_link")
        self.assertEqual(result_dict["content"][2]["type"], "image")
        self.assertEqual(result_dict["content"][3]["type"], "text")

    def test_call_tool_result_structured_content_dict(self):
        """Test CallToolResult with dict structured_content"""
        metadata = {
            "id": "123",
            "name": "Test",
            "tags": ["tag1", "tag2"],
            "count": 42
        }

        result = func.CallToolResult(
            content=[func.TextContentBlock(text="Data")],
            structured_content=metadata
        )

        result_dict = result.to_dict()
        self.assertEqual(result_dict["structuredContent"], metadata)
        self.assertEqual(result_dict["structuredContent"]["id"], "123")
        self.assertEqual(result_dict["structuredContent"]["count"], 42)

    def test_call_tool_result_structured_content_nested(self):
        """Test CallToolResult with nested structured_content"""
        nested_data = {
            "user": {
                "id": 1,
                "name": "John",
                "profile": {
                    "age": 30,
                    "location": "NYC"
                }
            },
            "metadata": {
                "timestamp": "2026-03-18T00:00:00Z"
            }
        }

        result = func.CallToolResult(
            content=[func.TextContentBlock(text="User data")],
            structured_content=nested_data
        )

        result_dict = result.to_dict()
        self.assertEqual(result_dict["structuredContent"]["user"]["name"], "John")
        self.assertEqual(result_dict["structuredContent"]["user"]["profile"]["age"], 30)

    def test_call_tool_result_structured_content_list(self):
        """Test CallToolResult with list as structured_content"""
        list_data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]

        result = func.CallToolResult(
            content=[func.TextContentBlock(text="Items")],
            structured_content=list_data
        )

        result_dict = result.to_dict()
        self.assertIsInstance(result_dict["structuredContent"], list)
        self.assertEqual(len(result_dict["structuredContent"]), 3)
        self.assertEqual(result_dict["structuredContent"][1]["name"], "Item 2")

    def test_call_tool_result_empty_content_list(self):
        """Test CallToolResult with empty content list"""
        result = func.CallToolResult(content=[])

        self.assertEqual(len(result.content), 0)
        result_dict = result.to_dict()
        self.assertEqual(result_dict["content"], [])

    def test_content_blocks_json_serialization(self):
        """Test that ContentBlocks can be JSON serialized"""
        import json

        blocks = [
            func.TextContentBlock(text="Hello"),
            func.ImageContentBlock(data="base64", mime_type="image/png"),
            func.ResourceLinkBlock(uri="https://example.com")
        ]

        # Convert to dicts and serialize
        blocks_dict = [block.to_dict() for block in blocks]
        json_str = json.dumps(blocks_dict)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0]["type"], "text")
        self.assertEqual(parsed[1]["mimeType"], "image/png")

    def test_call_tool_result_json_serialization(self):
        """Test that CallToolResult can be JSON serialized"""
        import json

        result = func.CallToolResult(
            content=[
                func.TextContentBlock(text="Test"),
                func.ImageContentBlock(data="abc123", mime_type="image/jpeg")
            ],
            structured_content={"key": "value", "number": 123}
        )

        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        self.assertIn("content", parsed)
        self.assertIn("structuredContent", parsed)
        self.assertEqual(parsed["structuredContent"]["key"], "value")

    def test_content_block_inheritance(self):
        """Test that all ContentBlock types inherit from ContentBlock"""
        text_block = func.TextContentBlock(text="test")
        image_block = func.ImageContentBlock(data="data", mime_type="image/png")
        resource_block = func.ResourceLinkBlock(uri="uri")

        self.assertIsInstance(text_block, func.ContentBlock)
        self.assertIsInstance(image_block, func.ContentBlock)
        self.assertIsInstance(resource_block, func.ContentBlock)

    def test_content_block_type_immutable(self):
        """Test that type field is set correctly and consistently"""
        text_block = func.TextContentBlock(text="test")
        image_block = func.ImageContentBlock(data="data", mime_type="image/png")
        resource_block = func.ResourceLinkBlock(uri="uri")

        # Type should be set via field(init=False)
        self.assertEqual(text_block.type, "text")
        self.assertEqual(image_block.type, "image")
        self.assertEqual(resource_block.type, "resource_link")

        # Verify in dict output
        self.assertEqual(text_block.to_dict()["type"], "text")
        self.assertEqual(image_block.to_dict()["type"], "image")
        self.assertEqual(resource_block.to_dict()["type"], "resource_link")


class TestAutoUseResultSchema(unittest.TestCase):
    """Tests for automatic use_result_schema detection"""

    def setUp(self):
        self.app = func.FunctionApp()

    def tearDown(self):
        self.app = None

    def test_auto_detect_resource_link_block(self):
        """Test auto-detection of ResourceLinkBlock return type"""
        @self.app.mcp_tool()
        def get_logo() -> func.ResourceLinkBlock:
            """Returns a logo"""
            return func.ResourceLinkBlock(uri="file://logo.png")

        trigger = get_logo._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_text_content_block(self):
        """Test auto-detection of TextContentBlock return type"""
        @self.app.mcp_tool()
        def get_text() -> func.TextContentBlock:
            """Returns text"""
            return func.TextContentBlock(text="Hello")

        trigger = get_text._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_image_content_block(self):
        """Test auto-detection of ImageContentBlock return type"""
        @self.app.mcp_tool()
        def get_image() -> func.ImageContentBlock:
            """Returns image"""
            return func.ImageContentBlock(data="base64", mime_type="image/png")

        trigger = get_image._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_call_tool_result(self):
        """Test auto-detection of CallToolResult return type"""
        @self.app.mcp_tool()
        def get_result() -> func.CallToolResult:
            """Returns CallToolResult"""
            return func.CallToolResult(content=[])

        trigger = get_result._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_list_content_block(self):
        """Test auto-detection of List[ContentBlock] return type"""
        from typing import List

        @self.app.mcp_tool()
        def get_multiple() -> List[func.ContentBlock]:
            """Returns multiple blocks"""
            return [func.TextContentBlock(text="test")]

        trigger = get_multiple._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_list_text_content_block(self):
        """Test auto-detection of List[TextContentBlock] return type"""
        from typing import List

        @self.app.mcp_tool()
        def get_texts() -> List[func.TextContentBlock]:
            """Returns text blocks"""
            return [func.TextContentBlock(text="test")]

        trigger = get_texts._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_optional_content_block(self):
        """Test auto-detection of Optional[ContentBlock] return type"""
        from typing import Optional

        @self.app.mcp_tool()
        def maybe_image() -> Optional[func.ImageContentBlock]:
            """Maybe returns image"""
            return None

        trigger = maybe_image._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_mcp_content_class(self):
        """Test auto-detection of @mcp_content decorated class"""
        @func.mcp_content
        class MyData:
            def __init__(self, value: str):
                self.value = value

        @self.app.mcp_tool()
        def get_data() -> MyData:
            """Returns custom data"""
            return MyData("test")

        trigger = get_data._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_no_auto_detect_string(self):
        """Test that plain string return type doesn't trigger auto-detection"""
        @self.app.mcp_tool()
        def get_string() -> str:
            """Returns string"""
            return "Hello"

        trigger = get_string._function._bindings[0]
        self.assertFalse(trigger.use_result_schema)

    def test_no_auto_detect_int(self):
        """Test that int return type doesn't trigger auto-detection"""
        @self.app.mcp_tool()
        def get_number() -> int:
            """Returns number"""
            return 42

        trigger = get_number._function._bindings[0]
        self.assertFalse(trigger.use_result_schema)

    def test_no_auto_detect_dict(self):
        """Test that dict return type doesn't trigger auto-detection"""
        @self.app.mcp_tool()
        def get_dict() -> dict:
            """Returns dict"""
            return {"key": "value"}

        trigger = get_dict._function._bindings[0]
        self.assertFalse(trigger.use_result_schema)

    def test_no_auto_detect_no_annotation(self):
        """Test that no return annotation doesn't trigger auto-detection"""
        @self.app.mcp_tool()
        def no_annotation():
            """No annotation"""
            return "test"

        trigger = no_annotation._function._bindings[0]
        self.assertFalse(trigger.use_result_schema)

    def test_explicit_use_result_schema_true(self):
        """Test that explicit use_result_schema=True is preserved"""
        @self.app.mcp_tool(use_result_schema=True)
        def explicit_true() -> str:
            """Explicit True"""
            return "test"

        trigger = explicit_true._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_explicit_use_result_schema_false(self):
        """Test that explicit use_result_schema=False works"""
        @self.app.mcp_tool(use_result_schema=False)
        def explicit_false() -> str:
            """Explicit False"""
            return "test"

        trigger = explicit_false._function._bindings[0]
        self.assertFalse(trigger.use_result_schema)

    def test_explicit_overrides_auto_detection(self):
        """Test that explicit value is not overridden by auto-detection"""
        @self.app.mcp_tool(use_result_schema=True)
        def override_test() -> func.ResourceLinkBlock:
            """Override test"""
            return func.ResourceLinkBlock(uri="test")

        trigger = override_test._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)


class TestStructuredContentInResponses(unittest.TestCase):
    """Tests for structuredContent field in MCP responses"""

    def setUp(self):
        self.app = func.FunctionApp()

    def tearDown(self):
        self.app = None

    def test_structured_content_in_call_tool_result(self):
        """Test that CallToolResult includes structuredContent"""
        import json
        import asyncio

        @self.app.mcp_tool()
        def test_func() -> func.CallToolResult:
            """Test function"""
            return func.CallToolResult(
                content=[func.TextContentBlock(text="test")],
                structured_content={"key": "value"}
            )

        # Get the wrapper function
        wrapper = test_func._function._func

        # Call the wrapper
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))

        # Parse the result
        result_obj = json.loads(result)

        # Verify structure
        self.assertIn("type", result_obj)
        self.assertIn("content", result_obj)
        self.assertIn("structuredContent", result_obj)
        self.assertEqual(result_obj["type"], "call_tool_result")
        self.assertIsNotNone(result_obj["structuredContent"])

    def test_structured_content_in_single_content_block(self):
        """Test that single ContentBlock includes structuredContent"""
        import json
        import asyncio

        @self.app.mcp_tool()
        def test_func() -> func.ResourceLinkBlock:
            """Test function"""
            return func.ResourceLinkBlock(uri="file://test.png", name="Test")

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))
        result_obj = json.loads(result)

        self.assertIn("structuredContent", result_obj)
        self.assertIsNotNone(result_obj["structuredContent"])

        # Verify structuredContent matches content
        content_obj = json.loads(result_obj["content"])
        structured_obj = json.loads(result_obj["structuredContent"])
        self.assertEqual(content_obj, structured_obj)

    def test_structured_content_in_list_content_blocks(self):
        """Test that List[ContentBlock] includes structuredContent"""
        import json
        import asyncio
        from typing import List

        @self.app.mcp_tool()
        def test_func() -> List[func.ContentBlock]:
            """Test function"""
            return [
                func.TextContentBlock(text="First"),
                func.TextContentBlock(text="Second")
            ]

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))
        result_obj = json.loads(result)

        self.assertIn("structuredContent", result_obj)
        self.assertIsNotNone(result_obj["structuredContent"])

        # Verify structuredContent matches content
        content_obj = json.loads(result_obj["content"])
        structured_obj = json.loads(result_obj["structuredContent"])
        self.assertEqual(content_obj, structured_obj)

    def test_structured_content_with_mcp_content_decorator(self):
        """Test that @mcp_content decorated class includes structuredContent"""
        import json
        import asyncio

        @func.mcp_content
        class MyData:
            def __init__(self, name: str, value: int):
                self.name = name
                self.value = value

        @self.app.mcp_tool()
        def test_func() -> MyData:
            """Test function"""
            return MyData("test", 42)

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))
        result_obj = json.loads(result)

        self.assertIn("structuredContent", result_obj)
        self.assertIsNotNone(result_obj["structuredContent"])

        # Verify structured content contains the data
        structured_obj = json.loads(result_obj["structuredContent"])
        self.assertEqual(structured_obj["name"], "test")
        self.assertEqual(structured_obj["value"], 42)


class TestPromptArgument(unittest.TestCase):
    """Unit tests for PromptArgument dataclass"""

    def test_prompt_argument_creation_all_fields(self):
        arg = PromptArgument(
            name="code",
            description="The code to review",
            required=True
        )
        self.assertEqual(arg.name, "code")
        self.assertEqual(arg.description, "The code to review")
        self.assertTrue(arg.required)

    def test_prompt_argument_creation_minimal(self):
        arg = PromptArgument(name="text")
        self.assertEqual(arg.name, "text")
        self.assertIsNone(arg.description)
        self.assertFalse(arg.required)

    def test_prompt_argument_to_dict_all_fields(self):
        arg = PromptArgument(
            name="language",
            description="Programming language",
            required=True
        )
        result = arg.to_dict()
        self.assertEqual(result, {
            "name": "language",
            "description": "Programming language",
            "required": True
        })

    def test_prompt_argument_to_dict_minimal(self):
        arg = PromptArgument(name="input")
        result = arg.to_dict()
        self.assertEqual(result, {
            "name": "input",
            "description": None,
            "required": False
        })

    def test_prompt_argument_to_dict_no_description(self):
        arg = PromptArgument(name="data", required=True)
        result = arg.to_dict()
        self.assertEqual(result["name"], "data")
        self.assertIsNone(result["description"])
        self.assertTrue(result["required"])


class TestMCPPromptTrigger(unittest.TestCase):
    """Unit tests for MCPPromptTrigger"""

    def test_mcp_prompt_trigger_valid_creation_all_fields(self):
        args_json = json.dumps([
            {"name": "code", "description": "Code to review", "required": True},
            {"name": "language", "description": "Programming language", "required": False}
        ], separators=(',', ':'))

        trigger = MCPPromptTrigger(
            name="context",
            prompt_name="code_review",
            prompt_arguments=args_json,
            title="Code Review",
            description="Review code for quality",
            metadata='{"version": "1.0"}',
            icons=[{"name": "code", "url": "https://example.com/icon.png"}],
            data_type=DataType.UNDEFINED,
            dummy_field="dummy"
        )

        self.assertEqual(trigger.get_binding_name(), "mcpPromptTrigger")
        dict_repr = trigger.get_dict_repr()

        self.assertEqual(dict_repr["name"], "context")
        self.assertEqual(dict_repr["promptName"], "code_review")
        self.assertEqual(dict_repr["title"], "Code Review")
        self.assertEqual(dict_repr["description"], "Review code for quality")
        self.assertEqual(dict_repr["metadata"], '{"version": "1.0"}')
        self.assertEqual(dict_repr["promptArguments"], args_json)
        self.assertEqual(dict_repr["type"], "mcpPromptTrigger")
        self.assertEqual(dict_repr["direction"], BindingDirection.IN)
        self.assertEqual(dict_repr["dummyField"], "dummy")

    def test_mcp_prompt_trigger_only_required_args_creation(self):
        args_json = json.dumps([], separators=(',', ':'))

        trigger = MCPPromptTrigger(
            name="context",
            prompt_name="simple_prompt",
            prompt_arguments=args_json
        )

        self.assertEqual(trigger.get_binding_name(), "mcpPromptTrigger")
        dict_repr = trigger.get_dict_repr()

        self.assertEqual(dict_repr["name"], "context")
        self.assertEqual(dict_repr["promptName"], "simple_prompt")
        self.assertEqual(dict_repr["promptArguments"], "[]")
        self.assertEqual(dict_repr["type"], "mcpPromptTrigger")

    def test_mcp_prompt_trigger_empty_arguments(self):
        trigger = MCPPromptTrigger(
            name="ctx",
            prompt_name="test",
            prompt_arguments="[]"
        )

        dict_repr = trigger.get_dict_repr()
        self.assertEqual(dict_repr["promptArguments"], "[]")

    def test_mcp_prompt_trigger_with_icons(self):
        icons = [
            {"name": "icon1", "url": "https://example.com/1.png"},
            {"name": "icon2", "url": "https://example.com/2.png"}
        ]

        trigger = MCPPromptTrigger(
            name="ctx",
            prompt_name="test",
            prompt_arguments="[]",
            icons=icons
        )

        dict_repr = trigger.get_dict_repr()
        self.assertEqual(dict_repr["icons"], icons)


class TestMcpPromptDecorator(unittest.TestCase):
    """Unit tests for mcp_prompt_trigger decorator"""

    def test_mcp_prompt_decorator_all_fields(self):
        app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

        @app.mcp_prompt_trigger(
            arg_name="context",
            prompt_name="code_review",
            prompt_arguments=[
                PromptArgument("code", "Code to review", True),
                PromptArgument("language", "Programming language", False)
            ],
            title="Code Review",
            description="Reviews code quality",
            metadata='{"version": "1.0"}',
            icons=[{"name": "code", "url": "https://example.com/icon.png"}]
        )
        def code_review_prompt(context: PromptInvocationContext) -> str:
            return "Reviewed"

        func_name = code_review_prompt.get_function_name()
        self.assertEqual(func_name, "code_review_prompt")

        bindings = code_review_prompt.get_bindings()
        self.assertEqual(len(bindings), 1)

        trigger = bindings[0]
        self.assertEqual(trigger.get_binding_name(), "mcpPromptTrigger")

        dict_repr = trigger.get_dict_repr()
        self.assertEqual(dict_repr["name"], "context")
        self.assertEqual(dict_repr["promptName"], "code_review")
        self.assertEqual(dict_repr["title"], "Code Review")
        self.assertEqual(dict_repr["description"], "Reviews code quality")

        # Verify arguments were serialized correctly
        args = json.loads(dict_repr["promptArguments"])
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0]["name"], "code")
        self.assertTrue(args[0]["required"])
        self.assertEqual(args[1]["name"], "language")
        self.assertFalse(args[1]["required"])

    def test_mcp_prompt_decorator_minimal(self):
        app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

        @app.mcp_prompt_trigger(
            arg_name="ctx",
            prompt_name="simple",
            prompt_arguments=[]
        )
        def simple_prompt(ctx: PromptInvocationContext) -> str:
            return "Done"

        bindings = simple_prompt.get_bindings()
        trigger = bindings[0]
        dict_repr = trigger.get_dict_repr()

        self.assertEqual(dict_repr["promptName"], "simple")
        self.assertEqual(dict_repr["promptArguments"], "[]")

    def test_mcp_prompt_decorator_with_one_argument(self):
        app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

        @app.mcp_prompt_trigger(
            arg_name="context",
            prompt_name="summarize",
            prompt_arguments=[PromptArgument("text", "Text to summarize", True)]
        )
        def summarize(context: PromptInvocationContext) -> str:
            text = context.arguments.get("text", "")
            return f"Summary of: {text}"

        bindings = summarize.get_bindings()
        trigger = bindings[0]
        dict_repr = trigger.get_dict_repr()

        args = json.loads(dict_repr["promptArguments"])
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0]["name"], "text")
        self.assertEqual(args[0]["description"], "Text to summarize")
        self.assertTrue(args[0]["required"])

    def test_mcp_prompt_decorator_multiple_arguments(self):
        app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

        @app.mcp_prompt_trigger(
            arg_name="context",
            prompt_name="translate",
            prompt_arguments=[
                PromptArgument("text", "Text to translate", True),
                PromptArgument("source_lang", "Source language", False),
                PromptArgument("target_lang", "Target language", True)
            ]
        )
        def translate(context: PromptInvocationContext) -> str:
            return "Translated"

        bindings = translate.get_bindings()
        trigger = bindings[0]
        dict_repr = trigger.get_dict_repr()

        args = json.loads(dict_repr["promptArguments"])
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0]["name"], "text")
        self.assertEqual(args[1]["name"], "source_lang")
        self.assertEqual(args[2]["name"], "target_lang")

    def test_mcp_prompt_decorator_arguments_serialization(self):
        """Ensure PromptArgument objects are properly serialized to JSON"""
        app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

        @app.mcp_prompt_trigger(
            arg_name="ctx",
            prompt_name="test",
            prompt_arguments=[
                PromptArgument("arg1", None, False),
                PromptArgument("arg2", "Description", True)
            ]
        )
        def test_func(ctx: PromptInvocationContext) -> str:
            return ""

        bindings = test_func.get_bindings()
        trigger = bindings[0]
        dict_repr = trigger.get_dict_repr()

        # Should be valid JSON string
        args_json = dict_repr["promptArguments"]
        args = json.loads(args_json)

        self.assertIsInstance(args, list)
        self.assertEqual(len(args), 2)

        # First argument with None description
        self.assertEqual(args[0]["name"], "arg1")
        self.assertIsNone(args[0]["description"])
        self.assertFalse(args[0]["required"])

        # Second argument with description
        self.assertEqual(args[1]["name"], "arg2")
        self.assertEqual(args[1]["description"], "Description")
        self.assertTrue(args[1]["required"])
