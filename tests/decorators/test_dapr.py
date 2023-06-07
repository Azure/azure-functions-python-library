#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import unittest

from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.dapr_function_app import DaprFunctionApp
from azure.functions.decorators.constants import DAPR_BINDING_TRIGGER, DAPR_SERVICE_INVOCATION_TRIGGER, DAPR_TOPIC_TRIGGER
from tests.decorators.testutils import assert_json


class TestDapr(unittest.TestCase):
    def setUp(self):
        self.dapr_func_app = DaprFunctionApp()

    def _get_user_function(self, app):
        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)
        return funcs[0]

    def test_dapr_service_invocation_trigger_default_args(self):
        app = self.dapr_func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                       method_name="dummy_method_name")
        
        def dummy():
            pass

        func = self._get_user_function(app)

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": DAPR_SERVICE_INVOCATION_TRIGGER,
                                         "name": "req",
                                         "methodName": "dummy_method_name"
                                     }
                                 ]
                                 })

    def test_dapr_binding_trigger_default_args(self):
        app = self.dapr_func_app

        @app.dapr_binding_trigger(arg_name="req",
                                       binding_name="dummy_binding_name")
        
        def dummy():
            pass

        func = self._get_user_function(app)

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": DAPR_BINDING_TRIGGER,
                                         "name": "req",
                                         "bindingName": "dummy_binding_name"
                                     }
                                 ]
                                 })

    def test_dapr_topic_trigger_default_args(self):
        app = self.dapr_func_app

        @app.dapr_topic_trigger(arg_name="req",
                                pub_sub_name="dummy_pub_sub_name",
                                topic="dummy_topic",
                                route="/dummy_route")
        
        def dummy():
            pass

        func = self._get_user_function(app)

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": DAPR_TOPIC_TRIGGER,
                                         "name": "req",
                                         "pubSubName": "dummy_pub_sub_name",
                                         "topic":"dummy_topic",
                                         "route":"/dummy_route"
                                     }
                                 ]
                                 })