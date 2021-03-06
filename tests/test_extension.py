# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from azure.functions.extension.func_extension_hooks import FuncExtensionHooks
import os
import unittest
from unittest.mock import MagicMock, patch
from logging import Logger

from azure.functions.extension import (
    FuncExtensionBase,
    ExtensionException,
    ExtensionMeta
)
from azure.functions._abc import Context


class TestFuncExtension(unittest.TestCase):

    def setUp(self):
        self.mock_script_root = os.path.join('/', 'home', 'site', 'wwwroot')
        self.mock_file_path = os.path.join(
            self.mock_script_root, 'HttpTrigger', '__init__.py'
        )
        extension_os_environ = os.environ.copy()
        extension_os_environ['AzureWebJobsScriptRoot'] = self.mock_script_root
        self.patch_os_environ = patch.dict('os.environ', extension_os_environ)
        self.patch_os_environ.start()

    def tearDown(self) -> None:
        self.patch_os_environ.stop()
        ExtensionMeta._info.clear()
        ExtensionMeta._func_exts.clear()
        ExtensionMeta._app_exts = None

    def test_new_extension_not_implement_init_should_fail(self):
        """An extension without __init__ should not be initialized
        """
        class NewExtension(FuncExtensionBase):
            pass

        # Initialize new extension without file path
        with self.assertRaises(TypeError):
            NewExtension()

    def test_new_extension_not_passing_filename_should_fail(self):
        """Instantiate an extension without __file__ in parameter should fail
        """
        class NewExtension(FuncExtensionBase):
            def __init__(self, file_path: str):
                # Initialize without super().__init__(file_path) fails
                super().__init__()

        # Initialize new extension without file path passing to super
        with self.assertRaises(TypeError):
            NewExtension('not_passed_to_super')

    def test_new_extension_invalid_path_should_fail(self):
        """The trigger name is derived from file script name. If an invalid
        path is provided, should throw exception.
        """
        class NewExtension(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

        # Customer try to register extension with invalid path name.
        # This should be pointing to a script __init__.py instead of a folder.
        with self.assertRaises(ExtensionException):
            NewExtension('some_invalid_path')

    def test_new_extension_should_be_invalid_in_root_folder(self):
        """Function trigger path /home/site/wwwroot/<trigger_name>/__init__.py,
        If the path does not match this pattern, should throw error
        """
        class NewExtension(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

        # Customer try to register extension with /home/site/wwwroot.
        # This should be pointing to a script __init__.py instead of a folder.
        with self.assertRaises(ExtensionException):
            NewExtension(self.mock_script_root)

    def test_new_extension_should_be_invalid_in_other_folder(self):
        """Function trigger path /home/site/wwwroot/<trigger_name>/__init__.py,
        If the path is not in /home/site/wwwroot, should throw error
        """
        class NewExtension(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

        # Customer try to register extension with /some/other/path.
        # This should be pointing to a script __init__.py instead of a folder.
        with self.assertRaises(ExtensionException):
            NewExtension(os.path.join('/', 'some', 'other', 'path'))

    def test_new_extension_initialize_with_correct_path(self):
        """Instantiate an extension with __file__ in parameter should succeed
        """
        class NewExtension(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

        ext_instance = NewExtension(self.mock_file_path)
        self.assertEqual(ext_instance._trigger_name, 'HttpTrigger')

    def test_new_extension_should_succeed_with_submodule(self):
        """Instantiate an extension with __file__ in parameter should succeed
        from a trigger subfolder
        """
        class NewExtension(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

        # Customer try to register extension with /home/site/wwwroot.
        # This should be pointing to a script __init__.py instead of a folder.
        ext_instance = NewExtension(
            os.path.join(
                self.mock_script_root, 'HttpTrigger', 'SubModule',
                '__init__.py'
            )
        )
        self.assertEqual(ext_instance._trigger_name, 'HttpTrigger')

    def test_extension_registration(self):
        """Instantiate an extension with full life-cycle hooks support
        should be registered into _func_exts
        """
        # Define extension
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

            def after_function_load(self,
                                    logger: Logger,
                                    function_name: str,
                                    function_directory: str,
                                    *args,
                                    **kwargs) -> None:
                logger.info('ok_after_function_load')

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before_invocation')

            def after_invocation(self, logger: Logger, context: Context,
                                 *args, **kwargs) -> None:
                logger.info('ok_after_invocation')

        # Instantiate Extension
        ext_instance = NewExtensionBeforeInvocation(self.mock_file_path)

        # Check function hooks registration
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')
        self.assertIsInstance(hooks, FuncExtensionHooks)

        # Check after_function_load
        hook_meta = hooks.after_function_load[0]
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.after_function_load)

        # Check before_invocation_hook
        hook_meta = hooks.before_invocation[0]
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.before_invocation)

        # Check after_invocation_hook
        hook_meta = hooks.after_invocation[0]
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.after_invocation)

    def test_partial_registration(self):
        """Instantiate an extension with full life-cycle hooks support
        should be registered into _func_exts
        """
        # Define extension with partial hooks support (e.g. after_invocation)
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

            def after_invocation(self, logger: Logger, context: Context,
                                 *args, **kwargs) -> None:
                logger.info('ok_after_invocation')

        # Instantiate Extension
        ext_instance = NewExtensionBeforeInvocation(self.mock_file_path)

        # Check after_invocation hook registration
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')
        hook_meta = hooks.after_invocation[0]
        self.assertIsInstance(hooks, FuncExtensionHooks)
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.after_invocation)

    def test_extension_method_should_be_executed(self):
        """Ensure the life-cycle hook execution should happen
        """
        # Define extension with partial hooks support (e.g. after_invocation)
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)
                self.is_after_invocation_executed = False

            def after_invocation(self, logger: Logger, context: Context,
                                 *args, **kwargs) -> None:
                logger.info('ok_after_invocation')
                self.is_after_invocation_executed = True

        # Instantiate Extension
        ext_instance = NewExtensionBeforeInvocation(self.mock_file_path)

        # Check after_invocation hook invocation
        mock_logger = MagicMock()
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')
        self.assertFalse(ext_instance.is_after_invocation_executed)
        hooks.after_invocation[0].ext_impl(mock_logger, {})
        self.assertTrue(ext_instance.is_after_invocation_executed)

    def test_registration_should_lowercase_the_trigger_name(self):
        """The ExtensionMeta should not be case sensitive
        """
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_name: str):
                super().__init__(file_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before_invocation')

        NewExtensionBeforeInvocation(self.mock_file_path)

        # Check if the hooks can be retrieved from lower-cased trigger name
        self.assertIsNotNone(ExtensionMeta._func_exts.get('httptrigger'))

    def test_extension_invocation_should_have_logger(self):
        """Test if the extension can use the logger
        """
        class NewExtensionBeforeAndAfter(FuncExtensionBase):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before_invocation')

        # Register extension in customer's
        NewExtensionBeforeAndAfter(self.mock_file_path)
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')

        # Check if the hook implementation executes
        mock_logger = MagicMock()
        hooks.before_invocation[0].ext_impl(logger=mock_logger, context={})
        mock_logger.info.assert_called_with('ok_before_invocation')

    def test_two_extensions_on_same_trigger(self):
        """Test if two extensions can be registered on the same trigger
        """
        class NewExtension1(FuncExtensionBase):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before_1')

        class NewExtension2(FuncExtensionBase):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def before_invocation(self, logger: Logger, context: Context,
                                  *args, **kwargs) -> None:
                logger.info('ok_before_2')

        # Check if both extensions are registered under the same hook
        NewExtension1(self.mock_file_path)
        NewExtension2(self.mock_file_path)
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')

        # Check if the before invocation hook matches metadata
        extension_names = map(
            lambda x: getattr(x, 'ext_name'),
            hooks.before_invocation
        )
        self.assertIn('NewExtension1', extension_names)
        self.assertIn('NewExtension2', extension_names)

    def test_backward_compatilbility_less_arguments(self):
        """Test if the existing extension implemented the interface with
        less arguments
        """
        class ExtensionWithLessArgument(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)
                self.executed = False

            # Drop arguments
            def before_invocation(self):
                self.executed = True

        # Check if the before invocation hook matches metadata
        ext_instance = ExtensionWithLessArgument(self.mock_file_path)
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')

        # Check if implementation works
        hook_meta = hooks.before_invocation[0]
        self.assertEqual(hook_meta.ext_name, 'ExtensionWithLessArgument')

        # Check if the hook implementation executes
        hook_meta.ext_impl()
        self.assertTrue(ext_instance.executed)
