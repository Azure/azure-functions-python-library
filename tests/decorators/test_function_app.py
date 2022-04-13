#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest
from unittest import mock

from azure.functions import WsgiMiddleware, AsgiMiddleware
from azure.functions.decorators.constants import HTTP_OUTPUT, HTTP_TRIGGER
from azure.functions.decorators.core import DataType, AuthLevel, \
    BindingDirection, SCRIPT_FILE_NAME
from azure.functions.decorators.function_app import FunctionBuilder, \
    FunctionApp, Function, Scaffold, BluePrint
from azure.functions.decorators.http import HttpTrigger, HttpOutput, \
    HttpMethod
from tests.decorators.test_core import DummyTrigger
from tests.decorators.testutils import assert_json


class TestFunction(unittest.TestCase):

    def setUp(self):
        def dummy():
            return "dummy"

        self.dummy = dummy
        self.func = Function(self.dummy, "dummy.py")

    def test_function_creation(self):
        self.assertEqual(self.func.get_user_function(), self.dummy)
        self.assertEqual(self.func.function_script_file, "dummy.py")

    def test_set_function_name(self):
        self.func.set_function_name("func_name")
        self.assertEqual(self.func.get_function_name(), "func_name")
        self.func.set_function_name()
        self.assertEqual(self.func.get_function_name(), "func_name")
        self.func.set_function_name("func_name_2")
        self.assertEqual(self.func.get_function_name(), "func_name_2")

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
        self.func.set_function_name("func_name")

        self.assertEqual(self.func.get_function_name(), "func_name")
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
        self.assertEqual(self.func.get_raw_bindings(), [
            '{"direction": "OUT", "dataType": "UNDEFINED", "type": "http", '
            '"name": "out"}',
            '{"direction": "IN", "dataType": "UNDEFINED", "type": '
            '"httpTrigger", "name": "req", "methods": ["GET", "POST"], '
            '"authLevel": "ANONYMOUS", "route": "dummy"}'])


class TestFunctionBuilder(unittest.TestCase):
    def setUp(self):
        def dummy():
            return "dummy"

        self.dummy = dummy
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

    def test_function_builder_creation(self):
        self.assertTrue(callable(self.fb))
        func = getattr(self.fb, "_function")
        self.assertEqual(self.fb._function.function_script_file, "dummy.py")
        self.assertEqual(func.get_user_function(), self.dummy)

    def test_validate_function_missing_trigger(self):
        with self.assertRaises(ValueError) as err:
            self.fb.configure_function_name('dummy').build()
            self.fb.build()

        self.assertEqual(err.exception.args[0],
                         "Function dummy does not have a trigger. A valid "
                         "function must have one and only one trigger "
                         "registered.")

    def test_validate_function_trigger_not_in_bindings(self):
        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED,
                              auth_level=AuthLevel.ANONYMOUS,
                              route='dummy')
        with self.assertRaises(ValueError) as err:
            self.fb.configure_function_name('dummy').add_trigger(trigger)
            getattr(self.fb, "_function").get_bindings().clear()
            self.fb.build()

        self.assertEqual(err.exception.args[0],
                         f"Function dummy trigger {trigger} not present"
                         f" in bindings {[]}")

    def test_validate_function_working(self):
        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED,
                              auth_level=AuthLevel.ANONYMOUS)
        self.fb.configure_function_name('dummy').add_trigger(trigger)
        self.fb.build()

    def test_build_function_http_route_default(self):
        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED,
                              auth_level=AuthLevel.ANONYMOUS)
        self.fb.configure_function_name('dummy_route').add_trigger(trigger)
        func = self.fb.build()

        self.assertEqual(func.get_trigger().route, "dummy_route")

    def test_build_function_with_name_and_bindings(self):
        test_trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                                   data_type=DataType.UNDEFINED,
                                   auth_level=AuthLevel.ANONYMOUS,
                                   route='dummy')
        test_input = HttpOutput(name='out', data_type=DataType.UNDEFINED)

        func = self.fb.configure_function_name('func_name').add_trigger(
            test_trigger).add_binding(test_input).build()

        self.assertEqual(func.get_function_name(), "func_name")
        assert_json(self, func, {
            "scriptFile": "dummy.py",
            "bindings": [
                {
                    "authLevel": AuthLevel.ANONYMOUS,
                    "type": HTTP_TRIGGER,
                    "direction": BindingDirection.IN,
                    "name": "req",
                    "dataType": DataType.UNDEFINED,
                    "route": "dummy",
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
        trigger = HttpTrigger(name='req', methods=(HttpMethod.GET,),
                              data_type=DataType.UNDEFINED)
        self.fb.configure_function_name('dummy').add_trigger(trigger)
        func = self.fb.build(auth_level=AuthLevel.ANONYMOUS)

        self.assertEqual(func.get_trigger().auth_level, AuthLevel.ANONYMOUS)


class TestScaffold(unittest.TestCase):
    def setUp(self):
        class DummyApp(Scaffold):
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
        self.assertEquals(self.dummy._function_builders, [])

    def test_dummy_app_trigger(self):
        @self.dummy.dummy_trigger(name="dummy")
        def dummy():
            return "dummy"

        self.assertEquals(len(self.dummy._function_builders), 1)
        func = self.dummy._function_builders[0].build()
        self.assertEquals(func.get_function_name(), "dummy")
        self.assertEquals(func.get_function_json(),
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
        self.func_app = FunctionApp(auth_level='ANONYMOUS')
        self.assertEqual(self.func_app.auth_level, AuthLevel.ANONYMOUS)

        self.func_app = FunctionApp(auth_level=AuthLevel.ADMIN)
        self.assertEqual(self.func_app.auth_level, AuthLevel.ADMIN)

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

    @mock.patch('azure.functions.decorators.function_app.FunctionApp'
                '._add_http_app')
    def test_add_asgi(self, add_http_app_mock):
        mock_asgi_app = object()
        FunctionApp(asgi_app=mock_asgi_app)

        add_http_app_mock.assert_called_once()
        self.assertIsInstance(add_http_app_mock.call_args[0][0],
                              AsgiMiddleware)
        self.assertEqual(add_http_app_mock.call_args[0][1], {})

    @mock.patch('azure.functions.decorators.function_app.FunctionApp'
                '._add_http_app')
    def test_add_wsgi(self, add_http_app_mock):
        mock_wsgi_app = object()
        FunctionApp(wsgi_app=mock_wsgi_app)

        add_http_app_mock.assert_called_once()
        self.assertIsInstance(add_http_app_mock.call_args[0][0],
                              WsgiMiddleware)
        self.assertEqual(add_http_app_mock.call_args[0][1], {})

    @mock.patch('azure.functions.decorators.function_app.FunctionApp'
                '._add_http_app')
    def test_add_http_args(self, add_http_app_mock):
        mock_wsgi_app = object()
        app_kwargs = {"methods": ["GET"]}
        FunctionApp(wsgi_app=mock_wsgi_app, app_kwargs=app_kwargs)

        self.assertEqual(add_http_app_mock.call_args[0][1], app_kwargs)

    def test_add_http_app(self):
        app = FunctionApp(asgi_app=object(),
                          app_kwargs={"methods": ["GET"],
                                      "auth_level": "ANONYMOUS",
                                      "trigger_arg_data_type":
                                          DataType.UNDEFINED,
                                      "output_arg_data_type":
                                          DataType.UNDEFINED})
        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)
        func = funcs[0]

        self.assertEqual(func.get_function_name(), "http_app_func")
        self.assertEqual(func.get_raw_bindings(), [
            '{"direction": "IN", "dataType": "UNDEFINED", "type": '
            '"httpTrigger", "name": '
            '"req", "methods": ["GET"], "authLevel": "ANONYMOUS", "route": '
            '"/{*route}"}',
            '{"direction": "OUT", "dataType": "UNDEFINED", "type": "http", '
            '"name": '
            '"$return"}'])
        self.assertEqual(func.get_bindings_dict(), {
            "bindings": [
                {
                    "authLevel": AuthLevel.ANONYMOUS,
                    "dataType": DataType.UNDEFINED,
                    "direction": BindingDirection.IN,
                    "methods": [HttpMethod.GET],
                    "name": "req",
                    "route": "/{*route}",
                    "type": HTTP_TRIGGER
                },
                {
                    "dataType": DataType.UNDEFINED,
                    "direction": BindingDirection.OUT,
                    "name": "$return",
                    "type": HTTP_OUTPUT
                }
            ]})

    def test_register_function_app_error(self):
        with self.assertRaises(TypeError) as err:
            FunctionApp().register_functions(FunctionApp())

        self.assertEqual(err.exception.args[0],
                         "functions can not be type of FunctionApp!")

    def test_register_blueprint(self):
        bp = BluePrint()

        @bp.schedule(arg_name="name", schedule="10****")
        def hello(name: str):
            return "hello"

        app = FunctionApp()
        app.register_functions(bp)

        self.assertEqual(len(app.get_functions()), 1)
        self.assertEqual(app.auth_level, AuthLevel.FUNCTION)
        self.assertEqual(app.app_script_file, SCRIPT_FILE_NAME)

    def test_register_blueprint_auth_level(self):
        bp = BluePrint(auth_level=AuthLevel.ANONYMOUS)

        @bp.route("name")
        def hello(name: str):
            return "hello"

        app = FunctionApp()
        app.register_functions(bp)

        self.assertEqual(len(app.get_functions()), 1)
        self.assertEqual(app.get_functions()[0].get_trigger().auth_level,
                         AuthLevel.ANONYMOUS)

    def test_register_app_auth_level(self):
        bp = BluePrint()

        @bp.route("name")
        def hello(name: str):
            return "hello"

        app = FunctionApp(auth_level=AuthLevel.ANONYMOUS)
        app.register_functions(bp)

        self.assertEqual(len(app.get_functions()), 1)
        self.assertEqual(app.get_functions()[0].get_trigger().auth_level,
                         AuthLevel.ANONYMOUS)
