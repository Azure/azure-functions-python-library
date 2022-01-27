#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import unittest

from azure.functions import Function
from azure.functions.decorators.core import DataType, AuthLevel, \
    BindingDirection
from azure.functions.decorators.function_app import FunctionBuilder, \
    FunctionsApp
from azure.functions.decorators.http import HttpTrigger, HttpMethod, HttpOutput


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
                             "correct behavior as a function can only have one "
                             "trigger. Existing registered trigger "
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
        self.assertEqual(str(self.func), json.dumps({
            "scriptFile": "dummy.py",
            "bindings": [
                {
                    "type": "http",
                    "direction": BindingDirection.OUT.value,
                    "name": "out",
                    "dataType": DataType.UNDEFINED.value
                },
                {
                    "authLevel": "ANONYMOUS",
                    "type": "httpTrigger",
                    "direction": BindingDirection.IN.value,
                    "name": "req",
                    "dataType": DataType.UNDEFINED.value,
                    "route": "dummy",
                    "methods": [str(HttpMethod.GET), str(HttpMethod.POST)]
                }
            ]
        }))


class TestFunctionBuilder(unittest.TestCase):
    def setUp(self):
        def dummy():
            return "dummy"

        self.dummy = dummy
        self.fb = FunctionBuilder(self.dummy, "dummy.py")

    def test_function_builder_creation(self):
        self.assertTrue(callable(self.fb))
        func = getattr(self.fb, "_function")
        self.assertEqual(func.function_script_file, "dummy.py")
        self.assertEqual(func.get_user_function(), self.dummy)

    def test_validate_function_name(self):
        with self.assertRaises(ValueError) as err:
            self.fb.build()

        self.assertEqual(err.exception.args[0],
                         "Function name is missing.")

    def test_validate_function_missing_trigger(self):
        with self.assertRaises(ValueError) as err:
            self.fb.configure_function_name('dummy').build()
            self.fb.build()

        self.assertEqual(err.exception.args[0],
                         "Function dummy does not have a trigger.")

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
                         f" in bindings []")

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
        self.assertEqual(str(func), json.dumps({
            "scriptFile": "dummy.py",
            "bindings": [
                {
                    "authLevel": "ANONYMOUS",
                    "type": "httpTrigger",
                    "direction": BindingDirection.IN.value,
                    "name": "req",
                    "dataType": DataType.UNDEFINED.value,
                    "route": "dummy",
                    "methods": [
                        "GET"
                    ]
                },
                {
                    "type": "http",
                    "direction": BindingDirection.OUT.value,
                    "name": "out",
                    "dataType": DataType.UNDEFINED.value
                }
            ]
        }))


class TestFunctionsApp(unittest.TestCase):
    def setUp(self):
        self.func_app = FunctionsApp(app_script_file='dummy.py')

    def test_get_no_functions(self):
        self.assertEqual(self.func_app.get_functions(), [])

    def test_route_no_args(self):
        app = self.func_app

        @app.function_name(name="dummy")
        @app.route()
        def dummy():
            pass

        self.assertEqual(len(app.get_functions()), 1)

        func = app.get_functions()[0]
        self.assertEqual(func.get_user_function().__name__, "dummy")
        self.assertEqual(str(func), json.dumps({
            "scriptFile": "dummy.py",
            "bindings": [
                {
                    "authLevel": "ANONYMOUS",
                    "type": "httpTrigger",
                    "direction": BindingDirection.IN.value,
                    "name": "req",
                    "dataType": DataType.UNDEFINED.value,
                    "route": "dummy",
                    "methods": [
                        "GET", "POST"
                    ]
                },
                {
                    "type": "http",
                    "direction": BindingDirection.OUT.value,
                    "name": "$return",
                    "dataType": DataType.UNDEFINED.value
                }
            ]
        }))

    def test_route_with_all_args(self):
        app = self.func_app

        @app.function_name(name="dummy")
        @app.route(trigger_arg_name='trigger_name', binding_arg_name='out',
                   trigger_arg_data_type=DataType.STRING,
                   output_arg_data_type=DataType.STRING,
                   methods=(HttpMethod.GET, HttpMethod.PATCH),
                   auth_level=AuthLevel.FUNCTION, route='dummy_route')
        def dummy():
            pass

        self.assertEqual(len(app.get_functions()), 1)
        func = app.get_functions()[0]
        self.assertEqual(func.get_user_function().__name__, "dummy")

        self.assertEqual(str(func), json.dumps({
            "scriptFile": "dummy.py",
            "bindings": [
                {
                    "authLevel": "FUNCTION",
                    "type": "httpTrigger",
                    "direction": BindingDirection.IN.value,
                    "name": "trigger_name",
                    "dataType": DataType.STRING.value,
                    "route": "dummy_route",
                    "methods": [
                        "GET", "PATCH"
                    ]
                },
                {
                    "type": "http",
                    "direction": BindingDirection.OUT.value,
                    "name": "out",
                    "dataType": DataType.STRING.value
                }
            ]
        }))
