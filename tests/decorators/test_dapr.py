#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.constants import DAPR_BINDING, \
    DAPR_BINDING_TRIGGER, DAPR_INVOKE, DAPR_PUBLISH, DAPR_SECRET, \
    DAPR_SERVICE_INVOCATION_TRIGGER, DAPR_STATE, DAPR_TOPIC_TRIGGER
from azure.functions.decorators.function_app import FunctionApp
from tests.utils.testutils import assert_json


class TestDapr(unittest.TestCase):
    def setUp(self):
        self.func_app = FunctionApp()

    def _get_user_function(self, app):
        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)
        return funcs[0]

    def test_dapr_service_invocation_trigger_default_args(self):
        app = self.func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                             method_name="dummy_method_name")
        def test_dapr_service_invocation_trigger_default_args():
            pass

        func = self._get_user_function(app)

        assert_json
        (
            self, func,
            {
                "scriptFile": "function_app.py",
                "bindings": [
                    {
                        "direction": BindingDirection.IN,
                        "type": DAPR_SERVICE_INVOCATION_TRIGGER,
                        "name": "req",
                        "methodName": "dummy_method_name"
                    }
                ]
            }
        )

    def test_dapr_binding_trigger_default_args(self):
        app = self.func_app

        @app.dapr_binding_trigger(arg_name="req",
                                  binding_name="dummy_binding_name")
        def test_dapr_binding_trigger_default_args():
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
        app = self.func_app

        @app.dapr_topic_trigger(arg_name="req",
                                pub_sub_name="dummy_pub_sub_name",
                                topic="dummy_topic",
                                route="/dummy_route")
        def test_dapr_topic_trigger_default_args():
            pass

        func = self._get_user_function(app)

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": DAPR_TOPIC_TRIGGER,
                                         "name": "req",
                                         "pubSubName": "dummy_pub_sub_name",
                                         "topic": "dummy_topic",
                                         "route": "/dummy_route"
                                     }
                                 ]
                                 })

    def test_dapr_state_input_binding(self):
        app = self.func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                             method_name="dummy")
        @app.dapr_state_input(arg_name="in",
                              state_store="dummy_state_store",
                              key="dummy_key")
        def test_dapr_state_input_binding():
            pass

        func = self._get_user_function(app)

        self.assertEqual(len(func.get_bindings()), 2)

        output = func.get_bindings()[0]

        self.assertEqual(output.get_dict_repr(), {
            "direction": BindingDirection.IN,
            "type": DAPR_STATE,
            "name": "in",
            "stateStore": "dummy_state_store",
            "key": "dummy_key"
        })

    def test_dapr_secret_input_binding(self):
        app = self.func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                             method_name="dummy")
        @app.dapr_secret_input(arg_name="in",
                               secret_store_name="dummy_secret_store_name",
                               key="dummy_key",
                               metadata="dummy_metadata")
        def test_dapr_secret_input_binding():
            pass

        func = self._get_user_function(app)

        self.assertEqual(len(func.get_bindings()), 2)

        output = func.get_bindings()[0]

        self.assertEqual(output.get_dict_repr(), {
            "direction": BindingDirection.IN,
            "type": DAPR_SECRET,
            "name": "in",
            "secretStoreName": "dummy_secret_store_name",
            "key": "dummy_key",
            "metadata": "dummy_metadata"
        })

    def test_dapr_state_output_binding(self):
        app = self.func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                             method_name="dummy")
        @app.dapr_state_output(arg_name="out",
                               state_store="dummy_state_store",
                               key="dummy_key")
        def test_dapr_state_output_binding():
            pass

        func = self._get_user_function(app)

        self.assertEqual(len(func.get_bindings()), 2)

        output = func.get_bindings()[0]

        self.assertEqual(output.get_dict_repr(), {
            "direction": BindingDirection.OUT,
            "type": DAPR_STATE,
            "name": "out",
            "stateStore": "dummy_state_store",
            "key": "dummy_key"
        })

    def test_dapr_invoke_output_binding(self):
        app = self.func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                             method_name="dummy")
        @app.dapr_invoke_output(arg_name="out",
                                app_id="dummy_app_id",
                                method_name="dummy_method_name",
                                http_verb="dummy_http_verb")
        def test_dapr_invoke_output_binding():
            pass

        func = self._get_user_function(app)

        self.assertEqual(len(func.get_bindings()), 2)

        output = func.get_bindings()[0]

        self.assertEqual(output.get_dict_repr(), {
            "direction": BindingDirection.OUT,
            "type": DAPR_INVOKE,
            "name": "out",
            "appId": "dummy_app_id",
            "methodName": "dummy_method_name",
            "httpVerb": "dummy_http_verb"
        })

    def test_dapr_publish_output_binding(self):
        app = self.func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                             method_name="dummy")
        @app.dapr_publish_output(arg_name="out",
                                 pub_sub_name="dummy_pub_sub_name",
                                 topic="dummy_topic")
        def test_dapr_publish_output_binding():
            pass

        func = self._get_user_function(app)

        self.assertEqual(len(func.get_bindings()), 2)

        output = func.get_bindings()[0]

        self.assertEqual(output.get_dict_repr(), {
            "direction": BindingDirection.OUT,
            "type": DAPR_PUBLISH,
            "name": "out",
            "pubSubName": "dummy_pub_sub_name",
            "topic": "dummy_topic"
        })

    def test_dapr_binding_output_binding(self):
        app = self.func_app

        @app.dapr_service_invocation_trigger(arg_name="req",
                                             method_name="dummy")
        @app.dapr_binding_output(arg_name="out",
                                 binding_name="dummy_binding_name",
                                 operation="dummy_operation")
        def test_dapr_binding_output_binding():
            pass

        func = self._get_user_function(app)

        self.assertEqual(len(func.get_bindings()), 2)

        output = func.get_bindings()[0]

        self.assertEqual(output.get_dict_repr(), {
            "direction": BindingDirection.OUT,
            "type": DAPR_BINDING,
            "name": "out",
            "bindingName": "dummy_binding_name",
            "operation": "dummy_operation"
        })
