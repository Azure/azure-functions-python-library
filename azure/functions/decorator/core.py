import json
from typing import List, Dict, Union, Optional

from azure.functions.decorator._abc import Trigger, Binding, DummyTrigger, \
    StringifyEnum
from azure.functions.decorator.http import HttpTrigger, Http


class AuthLevel(StringifyEnum):
    FUNCTION = "function"
    ANONYMOUS = "anonymous"
    ADMIN = "admin"

class Function(object):
    def __init__(self, func, script_file=None):
        self._name = func.__name__
        self._func = func
        self._trigger: Optional[Trigger] = None
        self._bindings: List[Binding] = []

        self.function_script_file = script_file or "dummy"

    def add_binding(self, binding: Binding):
        self._bindings.append(binding)

    def add_trigger(self, trigger: Trigger):
        if self._trigger and not isinstance(self._trigger, DummyTrigger):
            raise ValueError("A trigger was already registered to this "
                             "function. Adding another trigger is not the "
                             "correct behavior as a function can only have one"
                             f" trigger. New trigger being added {trigger}")
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

    # TODO: Check function has trigger defined
    def validate_function(self):
        pass

    def __str__(self):
        return self.get_function_json()


class FunctionsApp:
    def __init__(self, app_script_file):
        self._functions: List[Function] = []
        self._app_script_file = app_script_file

    def get_functions(self) -> List[Function]:
        return self._functions

    def _validate_type(self, func):
        if isinstance(func, Function):
            f = self._functions.pop()
        elif callable(func):
            f = Function(func, self.app_script_file)
        else:
            raise ValueError("WTF Trigger!")
        return f

    def route(self, name: str, function_name: str = None):
        def decorator(func, *args, **kwargs):
            f = self._validate_type(func)
            f.set_function_name(function_name)
            f.add_trigger(trigger=HttpTrigger(name))
            f.add_binding(binding=Http())
            f.validate_function()
            self._functions.append(f)
            return f

        return decorator