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
