#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from abc import ABC
import inspect
import json
import unittest
from unittest import mock
from unittest.mock import patch

from azure.functions import WsgiMiddleware, AsgiMiddleware
from azure.functions.decorators.constants import HTTP_OUTPUT, HTTP_TRIGGER, \
    TIMER_TRIGGER
from azure.functions.decorators.core import DataType, AuthLevel, \
    BindingDirection, SCRIPT_FILE_NAME
from azure.functions.decorators.function_app import (
    BindingApi, FunctionBuilder, FunctionApp, Function, Blueprint,
    DecoratorApi, AsgiFunctionApp, SettingsApi, WsgiFunctionApp,
    HttpFunctionsAuthLevelMixin, FunctionRegister, TriggerApi,
    ExternalHttpFunctionApp
)
from azure.functions.decorators.http import HttpTrigger, HttpOutput, \
    HttpMethod
from azure.functions.decorators.retry_policy import RetryPolicy
from test_core import DummyTrigger
from tests.utils.testutils import assert_json


class TestFunction(unittest.TestCase):

    def setUp(self):
        def dummy():
            return "dummy"

        self.dummy = dummy
        self.func = Function(self.dummy, "dummy.py")

    def test_function_creation(self):
        self.assertEqual(self.func.get_user_function(), self.dummy)
        self.assertEqual(self.func.function_script_file, "dummy.py")

    def test_add_trigger(self):
        with self.assertRaises(ValueError) as err:
            trigger1 = HttpTrigger(name="req1", methods=(HttpMethod.GET,),
                                   data_type=DataType.UNDEFINED,
                                   auth_level=AuthLevel.ANONYMOUS,
                                   route="dummy")

            trigger2 = HttpTrigger(name="req2", methods=(HttpMethod.GET,),
                                   data_type=DataType.UNDEFINED,
                                   auth_level=AuthLevel.ANONYMOUS,
                                   route="dummy")

            self.func.add_trigger(trigger1)
            self.assertEqual(len(self.func.get_bindings()), 1)
            self.assertEqual(self.func.get_bindings()[0], trigger1)
            self.func.add_trigger(trigger2)
            self.assertEqual(err.exception,
                             "A trigger was already registered to this "
                             "function. Adding another trigger is not the "
                             "correct behavior as a function can only have one"
                             " trigger. Existing registered trigger "
                             f"is {trigger1} and New trigger "
                             f"being added is {trigger2}")

    def test_function_creation_with_binding_and_trigger(self):
        output = HttpOutput(name="out", data_type=DataType.UNDEFINED)
        trigger = HttpTrigger(name="req",
                              methods=(HttpMethod.GET, HttpMethod.POST),
                              data_type=DataType.UNDEFINED,
                              auth_level=AuthLevel.ANONYMOUS, route="dummy")
        self.func.add_binding(output)
        self.func.add_trigger(trigger)

        self.assertEqual(self.func.get_function_name(), "dummy")
        self.assertEqual(self.func.get_user_function(), self.dummy)
        assert_json(self, self.func, {"scriptFile": "dummy.py",
                                      "bindings": [
                                          {
                                              "type": HTTP_OUTPUT,
                                              "direction":
                                                  BindingDirection.OUT,
                                              "name": "out",
                                              "dataType": DataType.UNDEFINED
                                          },
                                          {
                                              "authLevel": AuthLevel.ANONYMOUS,
                                              "type": HTTP_TRIGGER,
                                              "direction": BindingDirection.IN,
                                              "name": "req",
                                              "dataType": DataType.UNDEFINED,
                                              "route": "dummy",
                                              "methods": [HttpMethod.GET,
                                                          HttpMethod.POST]
                                          }
                                      ]
                                      })

        raw_bindings = self.func.get_raw_bindings()
        self.assertEqual(len(raw_bindings), 2)
        raw_output_binding = raw_bindings[0]
        raw_trigger = raw_bindings[1]

        self.assertEqual(json.loads(raw_output_binding),
                         json.loads(
                             '{"direction": "OUT", "dataType": "UNDEFINED", '
                             '"type": "http", "name": "out"}'))

        self.assertEqual(json.loads(raw_trigger),
                         json.loads(
                             '{"direction": "IN", "dataType": "UNDEFINED", '
                             '"type": "httpTrigger", "authLevel": '
                             '"ANONYMOUS", "route": "dummy", "methods": ['
                             '"GET", "POST"], "name": "req"}'))


class TestFunctionBuilder(unittest.TestCase):

    def test_function_builder_creation(self):
        def test_function_builder_creation():
            return "dummy"

        self.dummy = test_function_builder_creation
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        self.assertTrue(callable(self.fb))
        func = getattr(self.fb, "_function")
        self.assertEqual(self.fb._function.function_script_file, "dummy.py")
        self.assertEqual(func.get_user_function(), self.dummy)

    def test_validate_function_missing_trigger(self):
        def test_validate_function_missing_trigger():
            return "dummy"

        self.dummy = test_validate_function_missing_trigger
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        with self.assertRaises(ValueError) as err:
            #  self.fb.configure_function_name('dummy').build()
            self.fb.build()

        self.assertEqual(err.exception.args[0],
                         "Function test_validate_function_missing_trigger"
                         " does not have a trigger. A valid function must have"
                         " one and only one trigger registered.")

    def test_validate_function_trigger_not_in_bindings(self):
        def test_validate_function_trigger_not_in_bindings():
            return "dummy"

        self.dummy = test_validate_function_trigger_not_in_bindings
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED,
                              auth_level=AuthLevel.ANONYMOUS,
                              route='dummy')
        with self.assertRaises(ValueError) as err:
            self.fb.add_trigger(trigger)
            getattr(self.fb, "_function").get_bindings().clear()
            self.fb.build()

        self.assertEqual(
            err.exception.args[0],
            f"Function test_validate_function_trigger_not_in_bindings"
            f" trigger {trigger} not present"
            f" in bindings {[]}")

    def test_validate_function_working(self):
        def test_validate_function_working():
            return "dummy"

        self.dummy = test_validate_function_working
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED,
                              auth_level=AuthLevel.ANONYMOUS,
                              route='test_validate_function_working')
        self.fb.add_trigger(trigger)
        self.fb.build()

    def test_build_function_http_route_default(self):
        def test_build_function_http_route_default():
            return "dummy"

        self.dummy = test_build_function_http_route_default
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED,
                              auth_level=AuthLevel.ANONYMOUS)
        self.fb.add_trigger(trigger)
        func = self.fb.build()

        self.assertEqual(func.get_trigger().route,
                         "test_build_function_http_route_default")

    def test_build_function_with_bindings(self):
        def test_build_function_with_bindings():
            return "dummy"

        self.dummy = test_build_function_with_bindings
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        test_trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                                   data_type=DataType.UNDEFINED,
                                   auth_level=AuthLevel.ANONYMOUS)
        test_input = HttpOutput(name='out', data_type=DataType.UNDEFINED)

        func = self.fb.add_trigger(
            test_trigger).add_binding(test_input).build()

        self.assertEqual(func.get_function_name(),
                         "test_build_function_with_bindings")
        assert_json(self, func, {
            "scriptFile": "dummy.py",
            "bindings": [
                {
                    "authLevel": AuthLevel.ANONYMOUS,
                    "type": HTTP_TRIGGER,
                    "direction": BindingDirection.IN,
                    "name": "req",
                    "dataType": DataType.UNDEFINED,
                    "route": "test_build_function_with_bindings",
                    "methods": [
                        HttpMethod.GET
                    ]
                },
                {
                    "type": HTTP_OUTPUT,
                    "direction": BindingDirection.OUT,
                    "name": "out",
                    "dataType": DataType.UNDEFINED
                }
            ]
        })

    def test_build_function_with_function_app_auth_level(self):
        def test_build_function_with_function_app_auth_level():
            return "dummy"

        self.dummy = test_build_function_with_function_app_auth_level
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED)
        self.fb.add_trigger(trigger)
        func = self.fb.build(auth_level=AuthLevel.ANONYMOUS)

        self.assertEqual(func.get_trigger().auth_level, AuthLevel.ANONYMOUS)

    def test_build_function_with_retry_policy_setting(self):
        def test_build_function_with_retry_policy_setting():
            return "dummy"

        self.dummy = test_build_function_with_retry_policy_setting
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

        setting = RetryPolicy(strategy="exponential", max_retry_count="2",
                              minimum_interval="1", maximum_interval="5")
        trigger = HttpTrigger(
            name='req', methods=(HttpMethod.GET,),
            data_type=DataType.UNDEFINED,
            auth_level=AuthLevel.ANONYMOUS,
            route='test_build_function_with_retry_policy_setting')
        self.fb.add_trigger(trigger)
        self.fb.add_setting(setting)
        func = self.fb.build()

        self.assertEqual(func.get_settings_dict("retry_policy"),
                         {'setting_name': 'retry_policy',
                          'strategy': 'exponential', 'max_retry_count': '2',
                          'minimum_interval': '1', 'maximum_interval': '5'})

    def test_unique_method_names(self):
        app = FunctionApp()

        @app.schedule(arg_name="name", schedule="10****")
        def test_unique_method_names(name: str):
            return name

        @app.schedule(arg_name="name", schedule="10****")
        def test_unique_method_names2(name: str):
            return name

        functions = app.get_functions()
        self.assertEqual(len(functions), 2)

        self.assertEqual(functions[0].get_function_name(),
                         "test_unique_method_names")
        self.assertEqual(functions[1].get_function_name(),
                         "test_unique_method_names2")

    def test_unique_function_names(self):
        app = FunctionApp()

        @app.function_name("test_unique_function_names")
        @app.schedule(arg_name="name", schedule="10****")
        def test_unique_function_names(name: str):
            return name

        @app.function_name("test_unique_function_names2")
        @app.schedule(arg_name="name", schedule="10****")
        def test_unique_function_names2(name: str):
            return name

        functions = app.get_functions()
        self.assertEqual(len(functions), 2)

        self.assertEqual(functions[0].get_function_name(),
                         "test_unique_function_names")
        self.assertEqual(functions[1].get_function_name(),
                         "test_unique_function_names2")

    def test_same_method_names(self):
        app = FunctionApp()

        @app.schedule(arg_name="name", schedule="10****") # NoQA
        def test_same_method_names(name: str): # NoQA
            return name

        @app.schedule(arg_name="name", schedule="10****") # NoQA
        def test_same_method_names(name: str): # NoQA
            return name

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(err.exception.args[0],
                         "Function test_same_method_names does not have"
                         " a unique function name."
                         " Please change @app.function_name()"
                         " or the function method name to be unique.")

    def test_same_function_names(self):
        app = FunctionApp()

        @app.function_name("test_same_function_names") # NoQA
        @app.schedule(arg_name="name", schedule="10****")
        def test_same_function_names(name: str):
            return name

        @app.function_name("test_same_function_names") # NoQA
        @app.schedule(arg_name="name", schedule="10****")
        def test_same_function_names(name: str): # NoQA
            return name

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(err.exception.args[0],
                         "Function test_same_function_names does not have"
                         " a unique function name."
                         " Please change @app.function_name()"
                         " or the function method name to be unique.")

    def test_same_function_name_different_method_name(self):
        app = FunctionApp()

        @app.function_name("test_same_function_name_different_method_name")
        @app.schedule(arg_name="name", schedule="10****")
        def test_same_function_name_different_method_name(name: str):
            return name

        @app.function_name("test_same_function_name_different_method_name")
        @app.schedule(arg_name="name", schedule="10****")
        def test_same_function_name_different_method_name2(name: str):
            return name

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(
            err.exception.args[0],
            "Function test_same_function_name_different_method_name"
            " does not have a unique function name."
            " Please change @app.function_name()"
            " or the function method name to be unique.")

    def test_same_function_and_method_name(self):
        app = FunctionApp()

        @app.function_name("test_same_function_and_method_name")
        @app.schedule(arg_name="name", schedule="10****")
        def test_same_function_and_method_name2(name: str):
            return name

        @app.schedule(arg_name="name", schedule="10****")
        def test_same_function_and_method_name(name: str):
            return name

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(err.exception.args[0],
                         "Function test_same_function_and_method_name"
                         " does not have a unique function name."
                         " Please change @app.function_name()"
                         " or the function method name to be unique.")

    def test_blueprint_unique_method_names(self):
        app = FunctionApp()

        @app.schedule(arg_name="name", schedule="10****")
        def test_blueprint_unique_method_names(name: str):
            return name

        bp = Blueprint()

        @bp.schedule(arg_name="name", schedule="10****")
        def test_blueprint_unique_method_names2(name: str):
            return name

        app.register_blueprint(bp)

        functions = app.get_functions()
        self.assertEqual(len(functions), 2)

        self.assertEqual(functions[0].get_function_name(),
                         "test_blueprint_unique_method_names")
        self.assertEqual(functions[1].get_function_name(),
                         "test_blueprint_unique_method_names2")

    def test_blueprint_unique_function_names(self):
        app = FunctionApp()

        @app.function_name("test_blueprint_unique_function_names")
        @app.schedule(arg_name="name", schedule="10****")
        def test_blueprint_unique_function_names(name: str):
            return name

        bp = Blueprint()

        @bp.function_name("test_blueprint_unique_function_names2")
        @bp.schedule(arg_name="name", schedule="10****")
        def test_blueprint_unique_function_names2(name: str):
            return name

        app.register_blueprint(bp)

        functions = app.get_functions()
        self.assertEqual(len(functions), 2)

        self.assertEqual(functions[0].get_function_name(),
                         "test_blueprint_unique_function_names")
        self.assertEqual(functions[1].get_function_name(),
                         "test_blueprint_unique_function_names2")

    def test_blueprint_same_method_names(self):
        app = FunctionApp()

        @app.schedule(arg_name="name", schedule="10****") # NoQA
        def test_blueprint_same_method_names(name: str): # NoQA
            return name

        bp = Blueprint()

        @bp.schedule(arg_name="name", schedule="10****") # NoQA
        def test_blueprint_same_method_names(name: str): # NoQA
            return name

        app.register_blueprint(bp)

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(err.exception.args[0],
                         "Function test_blueprint_same_method_names"
                         " does not have a unique function name."
                         " Please change @app.function_name()"
                         " or the function method name to be unique.")

    def test_blueprint_same_function_names(self):
        app = FunctionApp()

        @app.function_name("test_blueprint_same_function_names") # NoQA
        @app.schedule(arg_name="name", schedule="10****")
        def test_blueprint_same_function_names(name: str):  # NoQA
            return name

        bp = Blueprint()

        @bp.function_name("test_blueprint_same_function_names") # NoQA
        @bp.schedule(arg_name="name", schedule="10****")
        def test_blueprint_same_function_names(name: str):  # NoQA
            return name

        app.register_blueprint(bp)

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(err.exception.args[0],
                         "Function test_blueprint_same_function_names"
                         " does not have a unique function name. Please change"
                         " @app.function_name() or the function method name"
                         " to be unique.")

    def test_blueprint_same_function_name_different_method_name(self):
        app = FunctionApp()

        @app.function_name(
            "test_blueprint_same_function_name_different_method_name")
        @app.schedule(arg_name="name", schedule="10****")
        def test_blueprint_same_function_name_different_method_name(name: str):
            return name

        bp = Blueprint()

        @bp.function_name(
            "test_blueprint_same_function_name_different_method_name")
        @bp.schedule(arg_name="name", schedule="10****")
        def test_blueprint_same_function_name_different_method_name2(
                name: str):
            return name

        app.register_blueprint(bp)

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(
            err.exception.args[0],
            "Function test_blueprint_same_function_name_different_method_name"
            " does not have a unique function name. Please change"
            " @app.function_name() or the function method name to be unique.")

    def test_blueprint_same_function_and_method_name(self):
        app = FunctionApp()

        @app.function_name("test_blueprint_same_function_and_method_name")
        @app.schedule(arg_name="name", schedule="10****")
        def test_blueprint_same_function_and_method_name2(name: str):
            return name

        bp = Blueprint()

        @bp.schedule(arg_name="name", schedule="10****")
        def test_blueprint_same_function_and_method_name(name: str):
            return name

        app.register_blueprint(bp)

        with self.assertRaises(ValueError) as err:
            app.get_functions()
        self.assertEqual(
            err.exception.args[0],
            "Function test_blueprint_same_function_and_method_name"
            " does not have a unique function name."
            " Please change @app.function_name() or the function"
            " method name to be unique.")

    def test_user_function_is_directly_callable_no_args(self):
        def test_validate_function_working_no_args():
            return "dummy"

        self.dummy = test_validate_function_working_no_args
        self.fb = FunctionBuilder(self.dummy, "dummy.py")
        self.assertEqual(self.fb(), "dummy")

    def test_user_function_is_directly_callable_args(self):
        def test_validate_function_working_sum_args(arg1: int, arg2: int):
            return arg1 + arg2

        self.dummy = test_validate_function_working_sum_args
        self.fb = FunctionBuilder(self.dummy, "dummy.py")
        self.assertEqual(self.fb(1, 2), 3)


class TestScaffold(unittest.TestCase):
    def setUp(self):
        class DummyApp(DecoratorApi):
            def dummy_trigger(self, name: str):
                @self._configure_function_builder
                def wrap(fb):
                    def decorator():
                        fb.add_trigger(trigger=DummyTrigger(name=name))
                        return fb

                    return decorator()

                return wrap

        self.dummy = DummyApp()

    def test_has_app_script_file(self):
        self.assertTrue(self.dummy.app_script_file, SCRIPT_FILE_NAME)

    def test_has_function_builders(self):
        self.assertEqual(self.dummy._function_builders, [])

    def test_dummy_app_trigger(self):
        @self.dummy.dummy_trigger(name="dummy")
        def test_dummy_app_trigger():
            return "dummy"

        self.assertEqual(len(self.dummy._function_builders), 1)
        func = self.dummy._function_builders[0].build()
        self.assertEqual(func.get_function_name(), "test_dummy_app_trigger")
        self.assertEqual(func.get_function_json(),
                         '{"scriptFile": "function_app.py", "bindings": [{'
                         '"direction": "IN", "dataType": "UNDEFINED", '
                         '"type": "Dummy", "name": "dummy"}]}')


class TestFunctionApp(unittest.TestCase):
    def setUp(self):
        def dummy_func():
            pass

        self.dummy_func = dummy_func
        self.func_app = FunctionApp()

    def test_default_auth_level_function(self):
        self.assertEqual(self.func_app.auth_level, AuthLevel.FUNCTION)

    def test_default_script_file_path(self):
        self.assertEqual(self.func_app.app_script_file, SCRIPT_FILE_NAME)

    def test_auth_level(self):
        self.func_app = FunctionApp(http_auth_level='ANONYMOUS')
        self.assertEqual(self.func_app.auth_level, AuthLevel.ANONYMOUS)

    def test_get_no_functions(self):
        self.assertEqual(self.func_app.app_script_file, "function_app.py")
        self.assertEqual(self.func_app.get_functions(), [])

    def test_invalid_decorated_type(self):
        with self.assertRaises(ValueError) as err:
            self.func_app._validate_type(object())

        self.assertEqual(err.exception.args[0], "Unsupported type for "
                                                "function app decorator "
                                                "found.")

    def test_callable_decorated_type(self):
        fb = self.func_app._validate_type(self.dummy_func)
        self.assertTrue(isinstance(fb, FunctionBuilder))
        self.assertEqual(fb._function.get_user_function(), self.dummy_func)

    def test_function_builder_decorated_type(self):
        fb = FunctionBuilder(self.dummy_func, "dummy.py")
        self.func_app._function_builders.append(fb)

        fb = self.func_app._validate_type(fb)
        self.assertTrue(isinstance(fb, FunctionBuilder))
        self.assertEqual(fb._function.get_user_function(), self.dummy_func)

    @mock.patch('azure.functions.decorators.function_app.AsgiFunctionApp'
                '._add_http_app')
    def test_add_asgi(self, add_http_app_mock):
        mock_asgi_app = object()
        AsgiFunctionApp(app=mock_asgi_app, function_name='test_add_asgi')

        add_http_app_mock.assert_called_once()

        self.assertIsInstance(add_http_app_mock.call_args[0][0],
                              AsgiMiddleware)

    @mock.patch('azure.functions.decorators.function_app.WsgiFunctionApp'
                '._add_http_app')
    def test_add_wsgi(self, add_http_app_mock):
        mock_wsgi_app = object()
        WsgiFunctionApp(app=mock_wsgi_app, function_name='test_add_wsgi')

        add_http_app_mock.assert_called_once()
        self.assertIsInstance(add_http_app_mock.call_args[0][0],
                              WsgiMiddleware)

    def test_extends_required_classes(self):
        self.assertTrue(issubclass(ExternalHttpFunctionApp, FunctionRegister))
        self.assertTrue(issubclass(ExternalHttpFunctionApp, TriggerApi))
        self.assertTrue(issubclass(ExternalHttpFunctionApp, SettingsApi))
        self.assertTrue(issubclass(ExternalHttpFunctionApp, BindingApi))
        self.assertTrue(issubclass(ExternalHttpFunctionApp, ABC))
        self.assertTrue(issubclass(AsgiFunctionApp, ExternalHttpFunctionApp))
        self.assertTrue(issubclass(WsgiFunctionApp, ExternalHttpFunctionApp))

    def test_add_asgi_app(self):
        self._test_http_external_app(AsgiFunctionApp(
            app=object(),
            function_name='test_add_asgi_app'),
            True,
            function_name='test_add_asgi_app')

    def test_add_wsgi_app(self):
        self._test_http_external_app(WsgiFunctionApp(
            app=object(),
            function_name='test_add_wsgi_app'),
            False,
            function_name='test_add_wsgi_app')

    def test_register_function_app_error(self):
        with self.assertRaises(TypeError) as err:
            FunctionApp().register_functions(FunctionApp())

        self.assertEqual(err.exception.args[0],
                         "functions can not be type of FunctionRegister!")

    def test_register_blueprint(self):
        bp = Blueprint()

        @bp.schedule(arg_name="name", schedule="10****")
        def test_register_blueprint(name: str):
            return "hello"

        app = FunctionApp()
        app.register_blueprint(bp)

        self.assertEqual(len(app.get_functions()), 1)
        self.assertEqual(app.auth_level, AuthLevel.FUNCTION)
        self.assertEqual(app.app_script_file, SCRIPT_FILE_NAME)

    def test_register_app_auth_level(self):
        bp = Blueprint()

        @bp.route("name")
        def test_register_app_auth_level(name: str):
            return "hello"

        app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)
        app.register_blueprint(bp)

        functions = app.get_functions()
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0].get_trigger().auth_level,
                         AuthLevel.ANONYMOUS)

    def test_default_function_http_type(self):
        app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)

        @app.route("name")
        def hello(name: str):
            return "hello"

        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)

        func = funcs[0]
        self.assertEqual(func.http_type, 'function')

    def test_set_http_type(self):
        app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)

        @app.route("name1")
        @app.http_type("dummy1")
        def test_set_http_type(name: str):
            return "hello"

        @app.route("name2")
        @app.http_type("dummy2")
        def test_set_http_type2(name: str):
            return "hello"

        funcs = app.get_functions()
        self.assertEqual(len(funcs), 2)

        func1 = funcs[0]
        self.assertEqual(func1.http_type, 'dummy1')
        func2 = funcs[1]
        self.assertEqual(func2.http_type, 'dummy2')

    def test_decorator_api_basic_props(self):
        class DummyFunctionApp(DecoratorApi):
            pass

        app = DummyFunctionApp()

        self.assertEqual(app.app_script_file, SCRIPT_FILE_NAME)
        self.assertIsNotNone(getattr(app, "_validate_type", None))
        self.assertIsNotNone(getattr(app, "_configure_function_builder", None))

    def test_http_functions_auth_level_mixin(self):
        class DummyFunctionApp(HttpFunctionsAuthLevelMixin):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)

        self.assertTrue(hasattr(app, "auth_level"))
        self.assertEqual(app.auth_level, AuthLevel.ANONYMOUS)

    def test_function_register_basic_props(self):
        class DummyFunctionApp(FunctionRegister):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)

        self.assertEqual(app.app_script_file, SCRIPT_FILE_NAME)
        self.assertIsNotNone(getattr(app, "_validate_type", None))
        self.assertIsNotNone(getattr(app, "_configure_function_builder", None))
        self.assertIsNone(getattr(app, "_require_auth_level"))
        self.assertTrue(hasattr(app, "auth_level"))
        self.assertEqual(app.auth_level, AuthLevel.ANONYMOUS)

    def test_function_register_http_function_app(self):
        class DummyFunctionApp(FunctionRegister, TriggerApi):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)

        @app.route("name1")
        def hello1(name: str):
            return "hello"

        @app.schedule(arg_name="name", schedule="10****")
        def hello2(name: str):
            return "hello"

        @app.route("name1")
        def hello3(name: str):
            return "hello"

        self.assertIsNone(app._require_auth_level, None)
        app.get_functions()
        self.assertTrue(app._require_auth_level)

    def test_function_register_non_http_function_app(self):
        class DummyFunctionApp(FunctionRegister, TriggerApi):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)
        blueprint = Blueprint()

        @blueprint.schedule(arg_name="name", schedule="10****")
        def test_function_register_non_http_function_app(name: str):
            return name

        app.register_blueprint(blueprint)

        app.get_functions()
        self.assertFalse(app._require_auth_level)

    def test_blueprints_with_function_name(self):
        class DummyFunctionApp(FunctionRegister, TriggerApi):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)
        blueprint = Blueprint()

        @blueprint.function_name("timer_function")
        @blueprint.schedule(arg_name="name", schedule="10****")
        def hello(name: str):
            return name

        app.register_blueprint(blueprint)

        functions = app.get_functions()
        self.assertEqual(len(functions), 1)

        setting = functions[0].get_setting("function_name")

        self.assertEqual(setting.get_settings_value("function_name"),
                         "timer_function")

    def test_legacy_blueprints_with_function_name(self):
        class LegacyBluePrint(TriggerApi, BindingApi):
            pass

        class DummyFunctionApp(FunctionRegister, TriggerApi):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)
        blueprint = LegacyBluePrint()

        @blueprint.function_name("test_legacy_blueprints_with_function_name")
        @blueprint.schedule(arg_name="name", schedule="10****")
        def hello(name: str):
            return name

        app.register_blueprint(blueprint)

        functions = app.get_functions()
        self.assertEqual(len(functions), 1)

        setting = functions[0].get_setting("function_name")

        self.assertEqual(setting.get_settings_value("function_name"),
                         "test_legacy_blueprints_with_function_name")

    def test_function_register_register_function_register_error(self):
        class DummyFunctionApp(FunctionRegister):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)
        with self.assertRaises(TypeError) as err:
            app.register_functions(app)

        self.assertEqual(err.exception.args[0],
                         'functions can not be type of FunctionRegister!')

    def test_function_register_register_functions_from_blueprint(self):
        class DummyFunctionApp(FunctionRegister):
            pass

        app = DummyFunctionApp(auth_level=AuthLevel.ANONYMOUS)
        blueprint = Blueprint()

        @blueprint.schedule(arg_name="name", schedule="10****")
        def test_function_register_register_functions_from_blueprint(
                name: str):
            return name

        app.register_blueprint(blueprint)

        functions = app.get_functions()
        self.assertEqual(len(functions), 1)

        trigger = functions[0].get_trigger()

        self.assertEqual(trigger.type, TIMER_TRIGGER)
        self.assertEqual(trigger.schedule, "10****")
        self.assertEqual(trigger.name, "name")
        self.assertEqual(
            functions[0].get_function_name(),
            "test_function_register_register_functions_from_blueprint")
        self.assertEqual(functions[0].get_user_function()("timer"), "timer")

    def test_asgi_function_app_default(self):
        app = AsgiFunctionApp(app=object())
        self.assertEqual(app.auth_level, AuthLevel.FUNCTION)

    def test_asgi_function_app_custom(self):
        app = AsgiFunctionApp(app=object(),
                              http_auth_level=AuthLevel.ANONYMOUS)
        self.assertEqual(app.auth_level, AuthLevel.ANONYMOUS)

    def test_asgi_function_app_is_http_function(self):
        app = AsgiFunctionApp(app=object())
        funcs = app.get_functions()

        self.assertEqual(len(funcs), 1)
        self.assertTrue(funcs[0].is_http_function())

    def test_wsgi_function_app_default(self):
        app = WsgiFunctionApp(app=object())
        self.assertEqual(app.auth_level, AuthLevel.FUNCTION)

    def test_wsgi_function_app_custom(self):
        app = WsgiFunctionApp(app=object(),
                              http_auth_level=AuthLevel.ANONYMOUS)
        self.assertEqual(app.auth_level, AuthLevel.ANONYMOUS)

    def test_wsgi_function_app_is_http_function(self):
        app = WsgiFunctionApp(
            app=object(),
            function_name='test_wsgi_function_app_is_http_function')
        funcs = app.get_functions()

        self.assertEqual(len(funcs), 1)
        self.assertTrue(funcs[0].is_http_function())

    def test_asgi_function_app_add_wsgi_app(self):
        with self.assertRaises(TypeError) as err:
            app = AsgiFunctionApp(app=object(),
                                  http_auth_level=AuthLevel.ANONYMOUS)
            app._add_http_app(WsgiMiddleware(object()))

        self.assertEqual(err.exception.args[0],
                         "Please pass AsgiMiddleware instance as parameter.")

    def test_wsgi_function_app_add_asgi_app(self):
        with self.assertRaises(TypeError) as err:
            app = WsgiFunctionApp(app=object(),
                                  http_auth_level=AuthLevel.ANONYMOUS)
            app._add_http_app(AsgiMiddleware(object()))

        self.assertEqual(err.exception.args[0],
                         "Please pass WsgiMiddleware instance as parameter.")

    @patch("azure.functions.decorators.function_app.ExternalHttpFunctionApp"
           ".__abstractmethods__", set())
    def test_external_http_function_app(self):
        with self.assertRaises(NotImplementedError):
            app = ExternalHttpFunctionApp(auth_level=AuthLevel.ANONYMOUS)
            app._add_http_app(AsgiMiddleware(object()))

    def _test_http_external_app(self, app, is_async, function_name):
        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)
        func = funcs[0]
        self.assertEqual(func.get_function_name(), function_name)
        raw_bindings = func.get_raw_bindings()
        raw_trigger = raw_bindings[0]
        raw_output_binding = raw_bindings[0]
        self.assertEqual(inspect.iscoroutinefunction(func.get_user_function()),
                         is_async)
        self.assertEqual(json.loads(raw_trigger),
                         json.loads(
                             '{"direction": "IN", "type": "httpTrigger", '
                             '"authLevel": "FUNCTION", "route": "/{*route}", '
                             '"methods": ["GET", "POST", "DELETE", "HEAD", '
                             '"PATCH", "PUT", "OPTIONS"], "name": "req"}'))
        self.assertEqual(json.loads(raw_output_binding), json.loads(
            '{"direction": "IN", "type": "httpTrigger", "authLevel": '
            '"FUNCTION", "methods": ["GET", "POST", "DELETE", "HEAD", '
            '"PATCH", "PUT", "OPTIONS"], "name": "req", "route": "/{'
            '*route}"}'))
        self.assertEqual(func.get_bindings_dict(), {
            "bindings": [
                {
                    "authLevel": AuthLevel.FUNCTION,
                    "direction": BindingDirection.IN,
                    "methods": [HttpMethod.GET, HttpMethod.POST,
                                HttpMethod.DELETE,
                                HttpMethod.HEAD,
                                HttpMethod.PATCH,
                                HttpMethod.PUT, HttpMethod.OPTIONS],
                    "name": "req",
                    "route": "/{*route}",
                    "type": HTTP_TRIGGER
                },
                {
                    "direction": BindingDirection.OUT,
                    "name": "$return",
                    "type": HTTP_OUTPUT
                }
            ]})


class TestFunctionRegister(unittest.TestCase):
    def test_validate_empty_dict(self):
        def dummy():
            return "dummy"

        test_func = Function(dummy, "dummy.py")
        fr = FunctionRegister(auth_level="ANONYMOUS")
        fr.validate_function_names(functions=[test_func])

    def test_validate_unique_names(self):
        def dummy():
            return "dummy"

        def dummy2():
            return "dummy"

        test_func = Function(dummy, "dummy.py")
        test_func2 = Function(dummy2, "dummy.py")

        fr = FunctionRegister(auth_level="ANONYMOUS")
        fr.validate_function_names(
            functions=[test_func, test_func2])

    def test_validate_non_unique_names(self):
        def dummy():
            return "dummy"

        test_func = Function(dummy, "dummy.py")
        test_func2 = Function(dummy, "dummy.py")

        fr = FunctionRegister(auth_level="ANONYMOUS")
        with self.assertRaises(ValueError) as err:
            fr.validate_function_names(functions=[test_func, test_func2])
            self.assertEqual(err.exception.args[0],
                             "Function dummy does not have"
                             " a unique function name."
                             " Please change @app.function_name()"
                             " or the function method name to be unique.")
