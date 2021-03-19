# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from azure.functions.extension.app_extension_hooks import AppExtensionHooks
import os
import unittest
from unittest.mock import MagicMock, patch
from logging import Logger

from azure.functions.extension import FunctionExtensionException
from azure.functions.extension.app_extension_base import AppExtensionBase
from azure.functions.extension.func_extension_base import FuncExtensionBase
from azure.functions.extension.extension_meta import ExtensionMeta
from azure.functions.extension.extension_scope import ExtensionScope
from azure.functions.extension.extension_hook_meta import ExtensionHookMeta
from azure.functions.extension.func_extension_hooks import FuncExtensionHooks
from azure.functions._abc import Context


class TestExtensionMeta(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._instance = ExtensionMeta

    def tearDown(self) -> None:
        super().tearDown()
        self._instance._app_exts = None
        self._instance._func_exts.clear()
        self._instance._info.clear()

    def test_app_extension_should_register_to_app_exts(self):
        """When defining an application extension, it should be registered
        to application extension set in ExtensionMeta
        """
        # Define a new AppExtension
        NewAppExtension = _generate_new_app_extension(self._instance)

        # Check if the extension is actuall being loaded
        registered_post_function_load_exts = (
            self._instance._app_exts.post_function_load_app_level
        )
        self.assertEqual(
            registered_post_function_load_exts[0].ext_impl,
            NewAppExtension.post_function_load_app_level
        )

    def test_func_extension_should_register_to_func_exts(self):
        """When instantiating a function extension, it should be registered
        to function extension set in ExtensionMeta
        """
        # Define a new function extension
        NewFuncExtension = _generate_new_func_extension_class(self._instance)

        # Follow line should be executed from HttpTrigger/__init__.py script
        # Instantiate a new function extension
        ext_instance = NewFuncExtension()
        registered_post_function_load_exts = (
            self._instance._func_exts['httptrigger'].post_function_load[0]
        )
        self.assertEqual(
            registered_post_function_load_exts.ext_impl,
            ext_instance.post_function_load
        )

    def test_app_extension_base_should_not_be_registered(self):
        """When defining the app extension base, it should not be registerd
        since the base is not an actual application extension.
        """
        class AppExtensionBase(metaclass=self._instance):
            _scope = ExtensionScope.APPLICATION

        self.assertIsNone(self._instance._app_exts)

    def test_func_extension_base_should_not_be_registered(self):
        """When instantiating the func extension base, it should not be
        registered since the base is not an actual function extension.
        """
        class FuncExtensionBase(metaclass=self._instance):
            _scope = ExtensionScope.FUNCTION

        # Follow line should be executed from HttpTrigger/__init__.py script
        # Instantiate a new function extension base
        FuncExtensionBase()
        self.assertEqual(len(self._instance._func_exts), 0)

    def test_app_extension_instantiation_should_throw_error(self):
        """Application extension is operating on a class level, shouldn't be
        instantiate by trigger script
        """
        # Define a new AppExtension
        NewAppExtension = _generate_new_app_extension(self._instance)

        # Try instantiate the extension but it should fail
        with self.assertRaises(FunctionExtensionException):
            NewAppExtension()

    def test_invalid_scope_extension_instantiation_should_throw_error(self):
        """If the _scope is not defined in an extension, it is most likely
        an invalid extension
        """
        class InvalidExtension(metaclass=self._instance):
            pass

        with self.assertRaises(FunctionExtensionException):
            InvalidExtension()

    def test_get_function_hooks(self):
        """If a specific extension is registered in to a function, it should
        be able to retrieve it
        """
        extension_hook = self._instance._func_exts.setdefault(
            'httptrigger', FuncExtensionHooks(
                post_function_load=[],
                pre_invocation=[],
                post_invocation=[]
            )
        )

        extension_hook.post_function_load.append(
            ExtensionHookMeta(ext_impl=lambda: 'hello', ext_name='world')
        )

        hook = self._instance.get_function_hooks('HttpTrigger')
        self.assertEqual(hook.post_function_load[0].ext_impl(), 'hello')
        self.assertEqual(hook.post_function_load[0].ext_name, 'world')

    def test_get_application_hooks(self):
        """The application extension should be stored in self._app_hooks
        """
        hook_obj = AppExtensionHooks(
            post_function_load_app_level=[],
            pre_invocation_app_level=[],
            post_invocation_app_level=[]
        )
        self._instance._app_exts = hook_obj
        hooks = self._instance.get_application_hooks()
        self.assertEqual(id(hook_obj), id(hooks))

    def test_get_registered_extensions_json_empty(self):
        """Ensure the get extension json will return empty if there's nothing
        registered"""
        info_json = self._instance.get_registered_extensions_json()
        self.assertEqual(info_json, r'{}')

    def test_get_registered_extensions_json_function_ext(self):
        """Ensure the get extension json will return function ext info"""
        # Define a new function extension
        NewFuncExtension = _generate_new_func_extension_class(self._instance)

        # Instantiate the function extension as in a customer's code
        NewFuncExtension()
        info_json = self._instance.get_registered_extensions_json()
        self.assertEqual(
            info_json,
            r'{"FuncExtension": {"HttpTrigger": ["NewFuncExtension"]}}'
        )

    def test_get_registered_extension_json_application_ext(self):
        """Ensure the get extension json will return application ext info"""
        # Register a new application extension
        _generate_new_app_extension(self._instance)

        # The registration should be tracked in the info
        info_json = self._instance.get_registered_extensions_json()
        self.assertEqual(
            info_json,
            r'{"AppExtension": ["NewAppExtension"]}'
        )

    def test_get_extension_scope(self):
        """Test if ExtensionScope is properly retrieved"""
        # Register a new application extension
        NewAppExtension = _generate_new_app_extension(self._instance)

        scope = self._instance._get_extension_scope(NewAppExtension)
        self.assertEqual(scope, ExtensionScope.APPLICATION)

    def test_get_extenison_scope_not_set(self):
        """Test if ExtensionScope should be unknown when empty"""
        class InvalidExtension(metaclass=self._instance):
            pass

        scope = self._instance._get_extension_scope(InvalidExtension)
        self.assertEqual(scope, ExtensionScope.UNKNOWN)

    def test_set_hooks_for_function(self):
        """Instantiating a function extension will register the life-cycle
        hooks
        """
        # Define a new function extension
        NewFuncExtension = _generate_new_func_extension_class(self._instance)

        # Instantiate this as in HttpTrigger/__init__.py customer's code
        ext_instance = NewFuncExtension()
        self._instance._set_hooks_for_function('HttpTrigger', ext_instance)
        meta = self._instance._func_exts['httptrigger'].post_function_load[0]

        # Check extension name
        self.assertEqual(meta.ext_name, 'NewFuncExtension')

        # Check if the extension is executable
        meta.ext_impl(
            function_name='HttpTrigger',
            function_directory='/home/site/wwwroot/HttpTrigger'
        )
        self.assertTrue(ext_instance._post_function_load_executed)

    def test_set_hooks_for_application(self):
        """Create an application extension class will register the life-cycle
        hooks
        """
        # Register a new application extension
        NewAppExtension = _generate_new_app_extension(self._instance)

        self._instance._set_hooks_for_application(NewAppExtension)
        meta = self._instance._app_exts.post_function_load_app_level[0]

        # Check extension name
        self.assertEqual(meta.ext_name, 'NewAppExtension')

        # Check if extension is initialized and executable
        meta.ext_impl(function_name="HttpTrigger",
                      function_directory="/home/site/wwwroot")
        self.assertTrue(NewAppExtension._post_function_load_app_level_executed)

    def test_register_function_extension(self):
        """After intiializing, function extension should be recorded in
        func_exts and _info
        """
        # Define a new function extension
        NewFuncExtension = _generate_new_func_extension_class(self._instance)

        # The following line should be called by customer
        ext_instance = NewFuncExtension()
        self._instance._register_function_extension(ext_instance)

        # Check _func_exts should have lowercased trigger name
        self.assertIn('httptrigger', self._instance._func_exts)

        # Check _info should record the function extension
        self.assertIn(
            'HttpTrigger',
            self._instance._info.get('FuncExtension', {})
        )

    def test_register_application_extension(self):
        """After creating an application extension class, it should be recorded
        in app_exts and _info
        """
        # Register a new application extension
        _generate_new_app_extension(self._instance)

        # Check _app_exts should trigger_hook
        self.assertEqual(
            self._instance._app_exts.post_function_load_app_level[0].ext_name,
            'NewAppExtension'
        )

        # Check _info should record the application extension
        self.assertIn(
            'NewAppExtension', self._instance._info.get('AppExtension', [])
        )


class TestFuncExtensionBase(unittest.TestCase):

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
        with self.assertRaises(FunctionExtensionException):
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
        with self.assertRaises(FunctionExtensionException):
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
        with self.assertRaises(FunctionExtensionException):
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
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

            def post_function_load(self,
                                   function_name: str,
                                   function_directory: str,
                                   *args,
                                   **kwargs) -> None:
                print('ok_post_function_load')

            def pre_invocation(self, logger: Logger, context: Context,
                               *args, **kwargs) -> None:
                logger.info('ok_pre_invocation')

            def post_invocation(self, logger: Logger, context: Context,
                                *args, **kwargs) -> None:
                logger.info('ok_post_invocation')

        # Instantiate Extension
        ext_instance = NewExtensionBeforeInvocation(self.mock_file_path)

        # Check function hooks registration
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')
        self.assertIsInstance(hooks, FuncExtensionHooks)

        # Check post_function_load
        hook_meta = hooks.post_function_load[0]
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.post_function_load)

        # Check pre_invocation_hook
        hook_meta = hooks.pre_invocation[0]
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.pre_invocation)

        # Check post_invocation_hook
        hook_meta = hooks.post_invocation[0]
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.post_invocation)

    def test_partial_registration(self):
        """Instantiate an extension with full life-cycle hooks support
        should be registered into _func_exts
        """
        # Define extension with partial hooks support (e.g. post_invocation)
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)

            def post_invocation(self, logger: Logger, context: Context,
                                *args, **kwargs) -> None:
                logger.info('ok_post_invocation')

        # Instantiate Extension
        ext_instance = NewExtensionBeforeInvocation(self.mock_file_path)

        # Check post_invocation hook registration
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')
        hook_meta = hooks.post_invocation[0]
        self.assertIsInstance(hooks, FuncExtensionHooks)
        self.assertEqual(hook_meta.ext_name, ext_instance.__class__.__name__)
        self.assertEqual(hook_meta.ext_impl, ext_instance.post_invocation)

    def test_extension_method_should_be_executed(self):
        """Ensure the life-cycle hook execution should happen
        """
        # Define extension with partial hooks support (e.g. post_invocation)
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)
                self.is_post_invocation_executed = False

            def post_invocation(self, logger: Logger, context: Context,
                                *args, **kwargs) -> None:
                logger.info('ok_post_invocation')
                self.is_post_invocation_executed = True

        # Instantiate Extension
        ext_instance = NewExtensionBeforeInvocation(self.mock_file_path)

        # Check post_invocation hook invocation
        mock_logger = MagicMock()
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')
        self.assertFalse(ext_instance.is_post_invocation_executed)
        hooks.post_invocation[0].ext_impl(mock_logger, {})
        self.assertTrue(ext_instance.is_post_invocation_executed)

    def test_registration_should_lowercase_the_trigger_name(self):
        """The ExtensionMeta should not be case sensitive
        """
        class NewExtensionBeforeInvocation(FuncExtensionBase):
            def __init__(self, file_name: str):
                super().__init__(file_name)

            def pre_invocation(self, logger: Logger, context: Context,
                               *args, **kwargs) -> None:
                logger.info('ok_pre_invocation')

        NewExtensionBeforeInvocation(self.mock_file_path)

        # Check if the hooks can be retrieved from lower-cased trigger name
        self.assertIsNotNone(ExtensionMeta._func_exts.get('httptrigger'))

    def test_extension_invocation_should_have_logger(self):
        """Test if the extension can use the logger
        """
        class NewExtensionBeforeAndAfter(FuncExtensionBase):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def pre_invocation(self, logger: Logger, context: Context,
                               *args, **kwargs) -> None:
                logger.info('ok_pre_invocation')

        # Register extension in customer's
        NewExtensionBeforeAndAfter(self.mock_file_path)
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')

        # Check if the hook implementation executes
        mock_logger = MagicMock()
        hooks.pre_invocation[0].ext_impl(logger=mock_logger, context={})
        mock_logger.info.assert_called_with('ok_pre_invocation')

    def test_two_extensions_on_same_trigger(self):
        """Test if two extensions can be registered on the same trigger
        """
        class NewFuncExtension1(FuncExtensionBase):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def pre_invocation(self, logger: Logger, context: Context,
                               function_name: str, function_directory: str,
                               *args, **kwargs):
                return 'ok_before1'

        class NewFuncExtension2(FuncExtensionBase):
            def __init__(self, trigger_name: str):
                super().__init__(trigger_name)

            def pre_invocation(self, logger: Logger, context: Context,
                               function_name: str, function_directory: str,
                               *args, **kwargs):
                return 'ok_before2'

        # Check if both extensions are registered under the same hook
        NewFuncExtension1(self.mock_file_path)
        NewFuncExtension2(self.mock_file_path)
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')

        # Check if the before invocation hook matches metadata
        extension_names = map(
            lambda x: getattr(x, 'ext_name'),
            hooks.pre_invocation
        )
        self.assertIn('NewFuncExtension1', extension_names)
        self.assertIn('NewFuncExtension2', extension_names)

        # Check if the extension can be executed correctly
        extension_implementations = list(map(
            lambda x: getattr(x, 'ext_impl'),
            hooks.pre_invocation
        ))
        self.assertEqual(
            extension_implementations[0](
                logger=None, context={}, function_name='HttpTrigger',
                function_directory='/home/site/wwwroot/HttpTrigger'
            ), 'ok_before1'
        )
        self.assertEqual(
            extension_implementations[1](
                logger=None, context={}, function_name='HttpTrigger',
                function_directory='/home/site/wwwroot/HttpTrigger'
            ), 'ok_before2'
        )

    def test_backward_compatilbility_less_arguments(self):
        """Test if the existing extension implemented the interface with
        less arguments
        """
        class ExtensionWithLessArgument(FuncExtensionBase):
            def __init__(self, file_path: str):
                super().__init__(file_path)
                self.executed = False

            # Drop arguments
            def pre_invocation(self):
                self.executed = True

        # Check if the before invocation hook matches metadata
        ext_instance = ExtensionWithLessArgument(self.mock_file_path)
        hooks = ExtensionMeta.get_function_hooks('HttpTrigger')

        # Check if implementation works
        hook_meta = hooks.pre_invocation[0]
        self.assertEqual(hook_meta.ext_name, 'ExtensionWithLessArgument')

        # Check if the hook implementation executes
        hook_meta.ext_impl()
        self.assertTrue(ext_instance.executed)


class TestAppExtensionBase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self._instance = ExtensionMeta
        self.patch_os_environ = patch.dict('os.environ', os.environ.copy())
        self.patch_os_environ.start()

    def tearDown(self) -> None:
        super().tearDown()
        self.patch_os_environ.stop()
        ExtensionMeta._app_exts = None
        ExtensionMeta._info.clear()
        ExtensionMeta._func_exts.clear()

    def test_empty_app_extension_should_pass(self):
        """An application extension can be registered directly since it never
        gets instantiate. Defining a new AppExtension should not raise an
        exception.
        """
        class NewEmptyAppExtension(AppExtensionBase):
            pass

    def test_init_method_should_be_called(self):
        """An application extension's init() classmethod should be called
        when the class is created"""
        # Define new an application extension
        NewAppExtension = _generate_new_app_extension(self._instance)

        # Ensure the init() method is executed
        self.assertTrue(NewAppExtension._init_executed)

    def test_extension_registration(self):
        """The life-cycles implementations in extension should be automatically
        registered in class creation
        """
        # Define new an application extension
        NewAppExtension = _generate_new_app_extension(self._instance)

        # Check app hooks registration
        hooks = self._instance.get_application_hooks()
        self.assertIsInstance(hooks, AppExtensionHooks)

        # Check post_function_load_app_level
        hook_meta = hooks.post_function_load_app_level[0]
        self.assertEqual(hook_meta.ext_name, 'NewAppExtension')
        self.assertEqual(hook_meta.ext_impl,
                         NewAppExtension.post_function_load_app_level)

        # Execute post_function_load_app_level
        hook_meta.ext_impl(
            logger=None, context={}, function_name='HttpTrigger',
            function_directory='/home/site/wwwroot/HttpTrigger'
        )
        self.assertTrue(
            NewAppExtension._post_function_load_app_level_executed
        )

        # Check pre_invocation_app_level
        hook_meta = hooks.pre_invocation_app_level[0]
        self.assertEqual(hook_meta.ext_name, 'NewAppExtension')
        self.assertEqual(hook_meta.ext_impl,
                         NewAppExtension.pre_invocation_app_level)

        # Execute pre_invocation_app_level
        hook_meta.ext_impl(logger=None, context={})
        self.assertTrue(
            NewAppExtension._pre_invocation_app_level
        )

        # Check post_invocation_app_level
        hook_meta = hooks.post_invocation_app_level[0]
        self.assertEqual(hook_meta.ext_name, 'NewAppExtension')
        self.assertEqual(hook_meta.ext_impl,
                         NewAppExtension.post_invocation_app_level)

        # Exectue post_invocation_app_level
        hook_meta.ext_impl(logger=None, context={})
        self.assertTrue(
            NewAppExtension._post_invocation_app_level
        )


def _generate_new_func_extension_class(
    metaclass: type,
    trigger_name: str = 'HttpTrigger'
):
    class NewFuncExtension(metaclass=metaclass):
        _scope = ExtensionScope.FUNCTION

        def __init__(self):
            self._trigger_name = trigger_name
            self._post_function_load_executed = False
            self._pre_invocation_executed = False
            self._post_invocation_executed = False

        def post_function_load(self, function_name, function_directory):
            self._post_function_load_executed = True

        def pre_invocation(self, logger, context):
            self._pre_invocation_executed = True

        def post_invocation(self, logger, context):
            self._post_invocation_executed = True

    return NewFuncExtension


def _generate_new_app_extension(metaclass: type):
    class NewAppExtension(metaclass=metaclass):
        _scope = ExtensionScope.APPLICATION

        _init_executed = False
        _post_function_load_app_level_executed = False
        _pre_invocation_app_level = False
        _post_invocation_app_level = False

        @classmethod
        def init(cls):
            cls._init_executed = True

        @classmethod
        def post_function_load_app_level(cls,
                                         function_name,
                                         function_directory,
                                         *args,
                                         **kwargs):
            cls._post_function_load_app_level_executed = True

        @classmethod
        def pre_invocation_app_level(cls, logger, context,
                                     *args, **kwargs):
            cls._pre_invocation_app_level = True

        @classmethod
        def post_invocation_app_level(cls, logger, context,
                                      *args, **kwargs):
            cls._post_invocation_app_level = True

    return NewAppExtension
