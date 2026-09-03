# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest.mock import patch

import azure.functions as func
from azure.functions.decorators.function_app import (
    AiApp,
    DurableAiApp,
    FunctionApp,
)


class TestAgentApps(unittest.TestCase):

    @patch('azure.functions.decorators.function_app._load_agents_base')
    def test_function_app_markdown_agent_delegates_exact_arguments(
            self, load_agents_base):
        agents_base = load_agents_base.return_value
        decorator = object()
        agents_base.markdown_agent.return_value = decorator
        app = FunctionApp()

        result = app.markdown_agent(
            provider='agent_framework',
            arg_name='agent',
            agent_name='orders',
            client_factory='factory',
        )

        self.assertIs(result, decorator)
        agents_base.markdown_agent.assert_called_once_with(
            app,
            provider='agent_framework',
            arg_name='agent',
            agent_name='orders',
            client_factory='factory',
        )

    @patch('azure.functions.decorators.function_app._load_agents_base')
    def test_ai_app_configures_provider_and_defaults(self, load_agents_base):
        agents_base = load_agents_base.return_value

        app = AiApp(
            provider='agent_framework',
            app_root='app',
            client_factory='factory',
        )

        agents_base.configure_app.assert_called_once_with(
            app,
            provider='agent_framework',
            app_root='app',
            provider_options={'client_factory': 'factory'},
        )

    @patch('azure.functions.decorators.function_app._load_agents_base')
    def test_ai_app_markdown_agent_uses_configured_provider(
            self, load_agents_base):
        agents_base = load_agents_base.return_value
        app = AiApp(provider='agent_framework')
        agents_base.reset_mock()

        app.markdown_agent(arg_name='agent', agent_name='orders')

        agents_base.markdown_agent.assert_called_once_with(
            app,
            provider='agent_framework',
            arg_name='agent',
            agent_name='orders',
        )

    @patch('azure.functions.decorators.function_app._load_agents_base')
    def test_ai_app_markdown_agent_can_override_configured_provider(
            self, load_agents_base):
        agents_base = load_agents_base.return_value
        app = AiApp(provider='agent_framework')
        agents_base.reset_mock()

        app.markdown_agent(
            provider='langgraph',
            arg_name='agent',
            agent_name='researcher',
        )

        agents_base.markdown_agent.assert_called_once_with(
            app,
            provider='langgraph',
            arg_name='agent',
            agent_name='researcher',
        )

    @patch('azure.functions.decorators.function_app._load_agents_base')
    def test_durable_ai_app_configures_durable_support(
            self, load_agents_base):
        agents_base = load_agents_base.return_value

        app = DurableAiApp(provider='agent_framework')

        agents_base.configure_durable_app.assert_called_once_with(app)

    @patch('azure.functions.decorators.function_app._load_agents_base')
    def test_durable_orchestration_delegates_to_base(
            self, load_agents_base):
        agents_base = load_agents_base.return_value
        sentinel = object()
        agents_base.durable_orchestration_trigger.return_value = sentinel
        app = DurableAiApp(provider='agent_framework')

        result = app.orchestration_trigger(
            context_name='context',
            orchestration='orders',
        )

        self.assertIs(result, sentinel)
        call = agents_base.durable_orchestration_trigger.call_args
        self.assertIs(call.args[0], app)
        self.assertEqual(call.kwargs['context_name'], 'context')
        self.assertEqual(call.kwargs['orchestration'], 'orders')
        self.assertIsNone(call.kwargs['input_type'])
        self.assertTrue(callable(call.kwargs['sdk_decorator']))

    def test_agent_apps_are_public(self):
        self.assertIs(func.AiApp, AiApp)
        self.assertIs(func.DurableAiApp, DurableAiApp)

    @patch('azure.functions.decorators._agents.importlib.import_module')
    def test_missing_provider_reports_extension_install(self, import_module):
        import_module.side_effect = ModuleNotFoundError(
            "No module named 'azurefunctions.extensions.agents.base'",
            name='azurefunctions.extensions.agents.base',
        )

        with self.assertRaises(ImportError) as raised:
            FunctionApp().markdown_agent(provider='agent_framework')

        self.assertEqual(
            str(raised.exception),
            "Agent provider 'agent_framework' is not installed. "
            "Install 'azurefunctions-extensions-agents-framework'.",
        )
        self.assertIs(raised.exception.__cause__, import_module.side_effect)

    @patch('azure.functions.decorators._agents.importlib.import_module')
    def test_missing_base_parent_reports_provider_install(self, import_module):
        import_module.side_effect = ModuleNotFoundError(
            "No module named 'azurefunctions'",
            name='azurefunctions',
        )

        with self.assertRaisesRegex(
                ImportError,
                'azurefunctions-extensions-agents-framework'):
            FunctionApp().markdown_agent(provider='agent_framework')

    @patch('azure.functions.decorators._agents.importlib.import_module')
    def test_provider_import_error_reports_extension_install(self, import_module):
        import_module.side_effect = ModuleNotFoundError(
            "No module named 'provider_dependency'",
            name='provider_dependency',
        )

        with self.assertRaisesRegex(
                ImportError,
                'azurefunctions-extensions-agents-framework') as raised:
            FunctionApp().markdown_agent(provider='agent_framework')

        self.assertIs(raised.exception.__cause__, import_module.side_effect)

    @patch('azure.functions.decorators.function_app._load_agents_base')
    def test_missing_durable_reports_provider_extra(self, load_agents_base):
        agents_base = load_agents_base.return_value
        agents_base.configure_durable_app.side_effect = ModuleNotFoundError(
            "No module named 'azure.durable_functions'",
            name='azure.durable_functions',
        )

        with self.assertRaisesRegex(
                ImportError,
                r'azurefunctions-extensions-agents-framework\[durable\]'):
            DurableAiApp(provider='agent_framework')


if __name__ == '__main__':
    unittest.main()
