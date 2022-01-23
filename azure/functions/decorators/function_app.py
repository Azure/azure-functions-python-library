#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

import json
from types import MethodType
from typing import Callable, Dict, List, Optional, Union, Tuple

from azure.functions.decorators.core import Binding, Trigger, DataType, \
    AuthLevel
from azure.functions.decorators.http import HttpTrigger, HttpOutput


class Function(object):
    def __init__(self, func: Callable, script_file):
        self._name = func.__name__
        self._func = func
        self._trigger: Optional[Trigger] = None
        self._bindings: List[Binding] = []

        self.function_script_file = script_file

    def add_binding(self, binding: Binding):
        self._bindings.append(binding)

    def add_trigger(self, trigger: Trigger):
        if self._trigger:
            raise ValueError("A trigger was already registered to this "
                             "function. Adding another trigger is not the "
                             "correct behavior as a function can only have one "
                             "trigger. Existing registered trigger "
                             f"is {self._trigger} and New trigger "
                             f"being added is {trigger}")
        self._trigger = trigger

        #  We still add the trigger info to the bindings to ensure that
        #  function.json is complete
        self._bindings.append(trigger)

    def set_function_name(self, function_name: str = None):
        if function_name:
            self._name = function_name

    def get_trigger(self):
        return self._trigger

    def get_bindings(self):
        return self._bindings

    def get_bindings_dict(self):
        stub_bindings_f_json: Dict[str, List[Dict]] = {"bindings": []}
        for b in self._bindings:
            stub_bindings_f_json["bindings"].append(b.get_dict_repr())
        return stub_bindings_f_json

    def get_dict_repr(self):
        stub_f_json: Dict[str, Union[List[str], str]] = {
            "scriptFile": self.function_script_file
        }
        stub_f_json.update(self.get_bindings_dict())  # NoQA
        return stub_f_json

    def get_user_function(self):
        return self._func

    def get_function_name(self):
        return self._name

    def get_function_json(self):
        return json.dumps(self.get_dict_repr())

    def __str__(self):
        return self.get_function_json()


class FunctionBuilder(object):
    def __init__(self, func, app_script_file):
        self._function = Function(func, app_script_file)

    def __call__(self, *args, **kwargs):
        pass

    def configure_function_name(self, function_name: str):
        self._function.set_function_name(function_name)
        return self

    def add_trigger(self, trigger: Trigger):
        self._function.add_trigger(trigger=trigger)
        return self

    def add_binding(self, binding: Binding):
        self._function.add_binding(binding=binding)
        return self

    def __validate_function(self) -> bool:
        return self._function.get_trigger() is not None

    def build(self):
        if not self.__validate_function():
            raise ValueError("Invalid function!")
        return self._function


class FunctionsApp:
    def __init__(self, app_script_file: str):
        self._function_builders: List[FunctionBuilder] = []
        self._app_script_file = app_script_file

    def get_functions(self) -> List[Function]:
        return [function_builder.build() for function_builder
                in self._function_builders]

    def __validate_type(self, func):
        if isinstance(func, FunctionBuilder):
            fb = self._function_builders.pop()
        elif callable(func):
            fb = FunctionBuilder(func, self._app_script_file)
        else:
            raise ValueError("WTF Trigger!")
        return fb

    def __configure_function_builder(self, wrap):
        def decorator(func):
            fb = self.__validate_type(func)
            self._function_builders.append(fb)
            return wrap(fb)

        return decorator

    def function_name(self, name: str):
        @self.__configure_function_builder
        def wrap(fb):
            def decorator():
                fb.configure_function_name(name)
                return fb

            return decorator()

        return wrap

    def http_trigger(self,
                     name: str,
                     data_type: Optional[DataType] = DataType.UNDEFINED,
                     methods: Optional[Tuple[MethodType]] = (),
                     auth_level: Optional[AuthLevel] = AuthLevel.ANONYMOUS,
                     route: Optional[str] = None):
        @self.__configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    HttpTrigger(name=name, data_type=data_type, methods=methods,
                                auth_level=auth_level, route=route))
                return fb

            return decorator()

        return wrap

    def http_output_binding(self,
                            name: str,
                            data_type: Optional[DataType] = DataType.UNDEFINED):
        @self.__configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(HttpOutput(name=name, data_type=data_type))
                return fb
            return decorator()
        return wrap

    # Old implementation for rollback if needed
    # def route(self, trigger_name: str, output_name: str, function_name: str):
    #     def decorator(func, *args, **kwargs):
    #         fb = self.__validate_type(func)
    #         fb.configure_function_name(function_name)
    #         fb.add_trigger(trigger=HttpTrigger(name=trigger_name))
    #         fb.add_binding(binding=HttpOutput(name=output_name))
    #         self._function_builders.append(fb)
    #         return fb
    #
    #     return decorator


# Uncomment to test the http decorators working as expected
# app = FunctionsApp("hello.txt")
#
#
# @app.function_name(name="test1")
# @app.http_trigger(name="req")
# @app.http_output_binding(name="resp")
# def hello_world(req) -> object:
#     print("hello")
#     resp = object()
#     return resp
#
# print(app.get_functions()[0].get_trigger())
# print(app.get_functions()[0].get_function_name())
# app.get_functions()[0].get_user_function()("hh")
