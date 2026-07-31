#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import typing
import unittest
import json
import asyncio
from dataclasses import dataclass
from unittest.mock import patch
from typing import List, Optional

import azure.functions as func
from azure.functions import (DataType, MCPToolContext,
                             PromptInvocationContext, PromptArgument)
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.mcp import (_MCPToolTrigger,
                                            MCPResourceTrigger,
                                            MCPPromptTrigger)
from azure.functions.mcp import (_MCPToolTriggerConverter,
                                 MCPResourceTriggerConverter,
                                 _is_mcp_sdk_type)
from azure.functions.meta import Datum
from mcp.types import (
    ResourceLink,
    TextContent,
    ImageContent,
    CallToolResult
)


class TestMCP(unittest.TestCase):
    def test_legacy_mcp_type_module_remains_supported(self):
        class LegacyMCPType:
            pass

        LegacyMCPType.__module__ = "mcp.types"

        self.assertTrue(_is_mcp_sdk_type(LegacyMCPType()))

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


class TestAutoUseResultSchema(unittest.TestCase):
    """Tests for automatic use_result_schema detection"""

    def setUp(self):
        self.app = func.FunctionApp()

    def tearDown(self):
        self.app = None

    def test_auto_detect_mcp_resource_link(self):
        """Test auto-detection of MCP SDK ResourceLink return type"""
        @self.app.mcp_tool()
        def get_logo() -> ResourceLink:
            """Returns a logo"""
            return ResourceLink(
                type="resource_link",
                uri="file://logo.png",
                name="Logo"
            )

        trigger = get_logo._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_mcp_text_content(self):
        """Test auto-detection of MCP SDK TextContent return type"""
        @self.app.mcp_tool()
        def get_text() -> TextContent:
            """Returns text"""
            return TextContent(type="text", text="Hello")

        trigger = get_text._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_mcp_image_content(self):
        """Test auto-detection of MCP SDK ImageContent return type"""
        @self.app.mcp_tool()
        def get_image() -> ImageContent:
            """Returns image"""
            return ImageContent(
                type="image",
                data="base64data",
                mimeType="image/png"
            )

        trigger = get_image._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_mcp_call_tool_result(self):
        """Test auto-detection of MCP SDK CallToolResult return type"""
        @self.app.mcp_tool()
        def get_result() -> CallToolResult:
            """Returns CallToolResult"""
            return CallToolResult(
                content=[TextContent(type="text", text="result")]
            )

        trigger = get_result._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_list_mcp_text_content(self):
        """Test auto-detection of List[TextContent] return type"""
        @self.app.mcp_tool()
        def get_texts() -> List[TextContent]:
            """Returns text blocks"""
            return [TextContent(type="text", text="test")]

        trigger = get_texts._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_list_union_mcp_types(self):
        """Test auto-detection of List[Union[MCP types]] return type"""
        from typing import Union

        @self.app.mcp_tool()
        def get_mixed_content() -> List[Union[TextContent, ImageContent]]:
            """Returns mixed content blocks"""
            return [TextContent(type="text", text="test")]

        trigger = get_mixed_content._function._bindings[0]
        self.assertTrue(trigger.use_result_schema)

    def test_auto_detect_optional_mcp_image_content(self):
        """Test auto-detection of Optional[ImageContent] return type"""
        @self.app.mcp_tool()
        def maybe_image() -> Optional[ImageContent]:
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


class TestStructuredContentInResponses(unittest.TestCase):
    """Tests for structuredContent field in MCP responses with official MCP SDK types"""

    def setUp(self):
        self.app = func.FunctionApp()

    def tearDown(self):
        self.app = None

    def test_structured_content_in_call_tool_result(self):
        """Test that MCP SDK CallToolResult includes structuredContent"""
        @self.app.mcp_tool()
        def test_func() -> CallToolResult:
            """Test function"""
            return CallToolResult(
                content=[TextContent(type="text", text="test")],
                structuredContent={"key": "value"}
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

        # Verify structuredContent value
        structured_obj = json.loads(result_obj["structuredContent"])
        self.assertEqual(structured_obj, {"key": "value"})

    def test_structured_content_in_resource_link(self):
        """Test that MCP SDK ResourceLink includes structuredContent"""
        @self.app.mcp_tool()
        def test_func() -> ResourceLink:
            """Test function"""
            return ResourceLink(
                type="resource_link",
                uri="file://test.png",
                name="Test",
                mimeType="image/png"
            )

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))
        result_obj = json.loads(result)

        self.assertIn("type", result_obj)
        self.assertIn("content", result_obj)
        self.assertIn("structuredContent", result_obj)
        self.assertEqual(result_obj["type"], "resource_link")
        self.assertIsNotNone(result_obj["structuredContent"])

        # Verify structuredContent matches content
        content_obj = json.loads(result_obj["content"])
        structured_obj = json.loads(result_obj["structuredContent"])
        self.assertEqual(content_obj, structured_obj)

    def test_structured_content_in_text_content(self):
        """Test that MCP SDK TextContent includes structuredContent"""
        @self.app.mcp_tool()
        def test_func() -> TextContent:
            """Test function"""
            return TextContent(type="text", text="Hello World")

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))
        result_obj = json.loads(result)

        self.assertIn("type", result_obj)
        self.assertEqual(result_obj["type"], "text")
        self.assertIn("content", result_obj)
        self.assertIn("structuredContent", result_obj)
        self.assertIsNotNone(result_obj["structuredContent"])

    def test_structured_content_with_mcp_content_decorator(self):
        """Test that @mcp_content decorated class includes structuredContent"""
        @func.mcp_content
        @dataclass
        class MyData:
            name: str
            value: int

        @self.app.mcp_tool()
        def test_func() -> MyData:
            """Test function"""
            return MyData(name="test", value=42)

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))
        result_obj = json.loads(result)

        self.assertIn("type", result_obj)
        self.assertIn("content", result_obj)
        self.assertIn("structuredContent", result_obj)
        self.assertIsNotNone(result_obj["structuredContent"])

        # Verify structured content contains the data
        structured_obj = json.loads(result_obj["structuredContent"])
        self.assertEqual(structured_obj["name"], "test")
        self.assertEqual(structured_obj["value"], 42)

    def test_backwards_compatibility_string_without_use_result_schema(self):
        """Test that plain string returns work without use_result_schema"""
        @self.app.mcp_tool()
        def test_func() -> str:
            """Test function"""
            return "Hello!"

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))

        # Should return the raw string, not a JSON structure
        self.assertEqual(result, "Hello!")
        self.assertIsInstance(result, str)

    def test_explicit_use_result_schema_with_string(self):
        """Test that explicit use_result_schema=True structures string response"""
        @self.app.mcp_tool(use_result_schema=True)
        def test_func() -> str:
            """Test function"""
            return "Hello!"

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))

        # Should return structured JSON
        result_obj = json.loads(result)
        self.assertIn("type", result_obj)
        self.assertIn("content", result_obj)
        self.assertIn("structuredContent", result_obj)

    def test_structured_content_in_list_of_mcp_types(self):
        """Test that List[MCP SDK types] includes structuredContent"""
        @self.app.mcp_tool()
        def test_func() -> List[TextContent]:
            """Test function"""
            return [
                TextContent(type="text", text="First item"),
                TextContent(type="text", text="Second item")
            ]

        wrapper = test_func._function._func
        context = json.dumps({"arguments": {}})
        result = asyncio.run(wrapper(context))
        result_obj = json.loads(result)

        # List of content blocks is wrapped as CallToolResult
        self.assertIn("type", result_obj)
        self.assertEqual(result_obj["type"], "call_tool_result")
        self.assertIn("content", result_obj)
        self.assertIn("structuredContent", result_obj)

        # Content contains the CallToolResult structure with the blocks
        content_obj = json.loads(result_obj["content"])
        self.assertIn("content", content_obj)
        self.assertEqual(len(content_obj["content"]), 2)
        self.assertEqual(content_obj["content"][0]["text"], "First item")
        self.assertEqual(content_obj["content"][1]["text"], "Second item")


class TestMCPPackageNotInstalled(unittest.TestCase):
    """Tests for graceful degradation when mcp package is not installed"""

    def setUp(self):
        self.app = func.FunctionApp()

    def tearDown(self):
        self.app = None

    def test_no_auto_detect_when_mcp_not_installed(self):
        """Test that auto-detection doesn't happen when mcp package is not available"""
        # Mock sys.modules to simulate mcp not being installed
        import sys
        with patch.dict(sys.modules, {'mcp': None, 'mcp.types': None}):
            # Clear any cached imports
            import importlib
            if 'azure.functions.decorators.function_app' in sys.modules:
                importlib.reload(sys.modules['azure.functions.decorators.function_app'])

            # Create a new app after mocking
            test_app = func.FunctionApp()

            @test_app.mcp_tool()
            def get_data() -> str:
                """Returns data"""
                return "test"

            trigger = get_data._function._bindings[0]
            # Should not auto-detect when mcp is not available
            self.assertFalse(trigger.use_result_schema)

    def test_mcp_content_decorator_still_works_without_mcp(self):
        """Test that @mcp_content decorator works even when mcp package is not installed"""
        @func.mcp_content
        class MyData:
            def __init__(self, value: str):
                self.value = value

        # Decorator should still mark the class
        self.assertTrue(hasattr(MyData, '__mcp_content__'))
        self.assertEqual(MyData.__mcp_content__, True)

    def test_explicit_use_result_schema_works_without_mcp(self):
        """Test that explicit use_result_schema=True works without mcp package"""
        @self.app.mcp_tool(use_result_schema=True)
        def test_func() -> str:
            """Test function"""
            return "Hello!"

        trigger = test_func._function._bindings[0]
        # Explicit parameter should always work
        self.assertTrue(trigger.use_result_schema)


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

        bindings = code_review_prompt._function._bindings
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

        bindings = simple_prompt._function._bindings
        trigger = bindings[0]
        dict_repr = trigger.get_dict_repr()

        self.assertEqual(dict_repr["promptName"], "simple")

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

        bindings = summarize._function._bindings
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

        bindings = translate._function._bindings
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

        bindings = test_func._function._bindings
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
