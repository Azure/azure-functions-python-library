#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import unittest

from azure.functions import Function
from azure.functions.decorators.core import Trigger, DataType, AuthLevel, \
    BindingDirection
from azure.functions.decorators.function_app import FunctionBuilder
from azure.functions.decorators.http import HttpTrigger, HttpMethod, HttpOutput


class TestFunction(unittest.TestCase):

    def setUp(self):
        def dummy():
            return "dummy"

        self.dummy = dummy
        self.func = Function(self.dummy, "dummy.py")

    def test_function_creation(self):
        self.assertEqual(self.func.get_function_name(), "dummy")
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
            trigger1 = HttpTrigger(name="req1", methods={HttpMethod.GET},
                                   data_type=DataType.UNDEFINED,
                                   auth_level=AuthLevel.ANONYMOUS,
                                   route="dummy")

            trigger2 = HttpTrigger(name="req2", methods={HttpMethod.GET},
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
        trigger = HttpTrigger(name="req", methods={HttpMethod.GET},
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
                    "methods": [
                        "GET"
                    ]
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

    def test_validate_function_missing_func_name(self):
        with self.assertRaises(ValueError) as err:
            self.fb.build()
            self.assertEqual(err.exception, "Function name is missing.")

    def test_validate_function_missing_trigger(self):
        with self.assertRaises(ValueError) as err:
            self.fb.configure_function_name("func_name")
            self.fb.build()
            self.assertEqual(err.exception,
                             f"Function func_name does not "
                             f"have a trigger.")
