# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest
from unittest.mock import MagicMock, call, patch
from logging import Logger

from azure.functions.extension import (
    FuncExtension,
    FuncExtensionHooks,
    FuncExtensionHookMeta
)
from azure.functions._abc import Context


class TestExtension(unittest.TestCase):

    def setUp(self):
        self.mock_script_root = '/home/site/wwwroot'
        self.patch_os_environ = patch.dict('os.environ', os.environ.copy())

        for trigger_name in FuncExtension._instances:
            FuncExtension._instances[trigger_name].before_invocation.clear()
            FuncExtension._instances[trigger_name].after_invocation.clear()

        self.patch_os_environ.start()

    def tearDown(self) -> None:
        self.patch_os_environ.stop()

    def test_new_extension_not_implement_init_should_fail(self):
        with self.assertRaises(TypeError):
            class NewExtension(FuncExtension):
                pass

            NewExtension()

    def test_new_extension_not_passing_filename_should_fail(self):
        with self.assertRaises(TypeError):
            class NewExtension(FuncExtension):
                def __init__(self, trigger_name: str):
                    super().__init__(trigger_name)

            NewExtension()

    def test_new_extension_should_initialize_properly(self):
        class NewExtension(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

        NewExtension('HttpTrigger')

    def test_before_invocation_registration(self):
        class NewExtensionBeforeInvocation(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before')

        NewExtensionBeforeInvocation('HttpTrigger')
        hooks = FuncExtension.get_hooks_of_trigger('HttpTrigger')
        self.assertIsInstance(hooks, FuncExtensionHooks)

        # Check if the invocation hook matches metadata
        hook_meta = hooks.before_invocation[0]
        self.assertIsInstance(hook_meta, FuncExtensionHookMeta)
        self.assertEqual(hook_meta.ext_name, 'NewExtensionBeforeInvocation')

        # Check if the hook implementation executes
        mock_logger = MagicMock()
        hook_meta.impl(logger=mock_logger, context={})
        mock_logger.info.assert_called_once_with('ok_before')

    def test_after_invocation_registration(self):
        class NewExtensionAfterInvocation(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def after_invocation(self, logger: Logger, context: Context,
                                 *args, **kwargs) -> None:
                logger.info('ok_after')

        NewExtensionAfterInvocation('HttpTrigger')
        hooks = FuncExtension.get_hooks_of_trigger('HttpTrigger')
        self.assertIsInstance(hooks, FuncExtensionHooks)

        # Check if the invocation hook matches metadata
        hook_meta = hooks.after_invocation[0]
        self.assertIsInstance(hook_meta, FuncExtensionHookMeta)
        self.assertEqual(hook_meta.ext_name, 'NewExtensionAfterInvocation')

        # Check if the hook implementation executes
        mock_logger = MagicMock()
        hook_meta.impl(logger=mock_logger, context={})
        mock_logger.info.assert_called_once_with('ok_after')

    def test_registration_should_lowercase_the_trigger_name(self):
        class NewExtensionBeforeInvocation(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before')

        NewExtensionBeforeInvocation('HttpTrigger')
        self.assertIsNotNone(FuncExtension._instances.get('httptrigger'))

    def test_register_both_before_and_after(self):
        class NewExtensionBeforeAndAfter(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before')

            def after_invocation(self, logger: Logger, context: Context,
                                 *args, **kwargs) -> None:
                logger.info('ok_after')

        NewExtensionBeforeAndAfter('HttpTrigger')
        hooks = FuncExtension.get_hooks_of_trigger('HttpTrigger')
        self.assertIsInstance(hooks, FuncExtensionHooks)

        # Check if the before invocation hook matches metadata
        before_meta = hooks.before_invocation[0]
        self.assertIsInstance(before_meta, FuncExtensionHookMeta)
        self.assertEqual(before_meta.ext_name, 'NewExtensionBeforeAndAfter')

        # Check if the after invocation hook matches metadata
        after_meta = hooks.after_invocation[0]
        self.assertIsInstance(after_meta, FuncExtensionHookMeta)
        self.assertEqual(after_meta.ext_name, 'NewExtensionBeforeAndAfter')

        # Check if the hook implementation executes
        mock_logger = MagicMock()
        before_meta.impl(logger=mock_logger, context={})
        after_meta.impl(logger=mock_logger, context={})
        mock_logger.info.assert_has_calls(
            (call('ok_before'), call('ok_after')),
            any_order=True
        )

    def test_two_extensions_on_same_trigger(self):
        class NewExtensionBefore1(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before_1')

        class NewExtensionBefore2(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before_2')

        NewExtensionBefore1('HttpTrigger')
        NewExtensionBefore2('HttpTrigger')
        hooks = FuncExtension.get_hooks_of_trigger('HttpTrigger')
        self.assertIsInstance(hooks, FuncExtensionHooks)

        # Check if the before invocation hook matches metadata
        before_meta1 = hooks.before_invocation[0]
        self.assertIsInstance(before_meta1, FuncExtensionHookMeta)
        self.assertEqual(before_meta1.ext_name, 'NewExtensionBefore1')

        # Check if the after invocation hook matches metadata
        before_meta2 = hooks.before_invocation[1]
        self.assertIsInstance(before_meta2, FuncExtensionHookMeta)
        self.assertEqual(before_meta2.ext_name, 'NewExtensionBefore2')

        # Check if the hook implementation executes
        mock_logger = MagicMock()
        before_meta1.impl(logger=mock_logger, context={})
        before_meta2.impl(logger=mock_logger, context={})
        mock_logger.info.assert_has_calls(
            (call('ok_before_1'), call('ok_before_2')),
            any_order=True
        )

    def test_backward_compatilbility_less_arguments(self):
        """Assume in the future we introduce more arguments to the hook.
        To test the backward compatibility of the existing extension, we should
        reduce its argument count
        """
        class NewExtensionWithExtraArgument(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            # Drop context argument
            def before_invocation(self, logger: Logger, *args, **kwargs):
                logger.info('ok')

        # Check if the before invocation hook matches metadata
        NewExtensionWithExtraArgument('HttpTrigger')
        hooks = FuncExtension.get_hooks_of_trigger('HttpTrigger')
        self.assertIsInstance(hooks, FuncExtensionHooks)

        # Check if implementation works
        hook_meta = hooks.before_invocation[0]
        self.assertEqual(hook_meta.ext_name, 'NewExtensionWithExtraArgument')

        # Check if the hook implementation executes
        mock_logger = MagicMock()
        hook_meta.impl(logger=mock_logger, context={})
        mock_logger.info.assert_called_once_with('ok')

    def test_register_to_trigger(self):
        class NewExtension(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok')

        # Customer try to register extension with register_to_trigger
        os.environ['AzureWebJobsScriptRoot'] = self.mock_script_root
        NewExtension.register_to_trigger(
            f'{self.mock_script_root}/HttpTrigger/__init__.py'
        )

        # Check if the extension name is HttpTrigger
        triggers = NewExtension.get_hooks_of_trigger('HttpTrigger')
        before_meta = triggers.before_invocation[0]
        self.assertEqual(before_meta.ext_name, 'NewExtension')

        # Check if the extension hook actually executes
        mock_logger = MagicMock()
        before_meta.impl(logger=mock_logger, context={})
        mock_logger.info.assert_called_once_with('ok')

    def test_register_to_trigger_no_azure_webjobs_script_root(self):
        class NewExtension(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok')

        # Customer try to register extension with register_to_trigger
        with self.assertRaises(ValueError):
            NewExtension.register_to_trigger(
                '/home/site/wwwroot/HttpTrigger/__init__.py'
            )

    def test_register_to_trigger_from_sub_folder_path(self):
        class NewExtension(FuncExtension):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok')

        # Customer try to register extension with register_to_trigger
        os.environ['AzureWebJobsScriptRoot'] = self.mock_script_root
        NewExtension.register_to_trigger(
            f'{self.mock_script_root}/HttpTrigger/sub_module/__init__.py'
        )

        # Trigger should still be HttpTrigger
        triggers = NewExtension.get_hooks_of_trigger('HttpTrigger')
        before_meta = triggers.before_invocation[0]
        self.assertEqual(before_meta.ext_name, 'NewExtension')

        # Check if the extension hook actually executes
        mock_logger = MagicMock()
        before_meta.impl(logger=mock_logger, context={})
        mock_logger.info.assert_called_once_with('ok')
