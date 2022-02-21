# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from typing import Dict

SCRIPT_FILE_NAME = "function_app.py"


class StringifyEnum(Enum):
    """This class output name of enum object when printed as string."""

    def __str__(self):
        return str(self.name)


class JsonDumpMeta(type):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        # setattr(cls, 'say_hi', cls.skip_none(cls.__dict__['say_hi']))
        cls.get_dict_repr = cls.skip_none(cls.get_dict_repr)
        return cls

    @staticmethod
    def skip_none(func):
        def wrapper(*args, **kw):
            res = func(*args, **kw)
            return JsonDumpMeta.clean_nones(res)

        return wrapper

    @staticmethod
    def clean_nones(value):
        """
        Recursively remove all None values from dictionaries and lists,
        and returns
        the result as a new dictionary or list.
        """
        if isinstance(value, list):
            return [JsonDumpMeta.clean_nones(x) for x in value if
                    x is not None]
        elif isinstance(value, dict):
            return {
                key: JsonDumpMeta.clean_nones(val)
                for key, val in value.items()
                if val is not None
            }
        else:
            return value


class FinalMeta(ABCMeta, JsonDumpMeta):
    pass


# Enums
class BindingDirection(StringifyEnum):
    """Direction of the binding used in function.json"""
    IN = 0
    """Input binding direction."""
    OUT = 1
    """Output binding direction."""
    INOUT = 2
    """Some bindings support a special binding direction. """


class DataType(StringifyEnum):
    """Data type of the binding used in function.json"""
    UNDEFINED = 0
    """Parse binding argument as string."""
    STRING = 1
    """Parse binding argument as binary."""
    BINARY = 2
    """Parse binding argument as stream."""
    STREAM = 3


class AuthLevel(StringifyEnum):
    """Azure HTTP authorization level, determines what keys, if any, need to
    be present on the request in order to invoke the function. """
    FUNCTION = "function"
    """A function-specific API key is required. This is the default value if
    none is provided. """
    ANONYMOUS = "anonymous"
    """No API key is required."""
    ADMIN = "admin"
    """The master key is required."""


class Cardinality(StringifyEnum):
    """Used for all non-C# languages. Set to many in order to enable
    batching. If omitted or set to one, a single message is passed to the
    function. """
    ONE = "one"
    """Singe message passed to the function."""
    MANY = "many"
    """Multiple messaged passed to the function per invocation."""


class AccessRights(StringifyEnum):
    """Access rights for the connection string. The default is manage,
    which indicates that the connection has the Manage permission. """
    MANAGE = "manage"
    """Confers the right to manage the topology of the namespace, including
    creating and deleting entities. """
    LISTEN = "listen"
    """Confers the right to listen (relay) or receive (queue, subscriptions)
    and all related message handling. """


class Binding(ABC):
    @staticmethod
    @abstractmethod
    def get_binding_name() -> str:
        pass

    def __init__(self, name: str,
                 direction: BindingDirection,
                 data_type: DataType,
                 is_trigger: bool):
        self.type = self.get_binding_name()
        self.is_trigger = is_trigger
        self.name = name
        self.direction = direction
        self.data_type = data_type

    @abstractmethod
    def get_dict_repr(self) -> Dict:
        pass

    def __str__(self) -> str:
        return str(self.get_dict_repr())


class Trigger(Binding, metaclass=FinalMeta):
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, is_trigger=True)


class InputBinding(Binding, metaclass=FinalMeta):
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, is_trigger=False)


class OutputBinding(Binding, metaclass=FinalMeta):
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.OUT,
                         name=name, data_type=data_type, is_trigger=False)
