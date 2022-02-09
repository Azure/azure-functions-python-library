# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from abc import ABC, ABCMeta, abstractmethod
from enum import Enum

# Constants
from typing import Dict

SCRIPT_FILE_NAME = "function_app.py"


class StringifyEnum(Enum):
    """This class output name of enum object when printed as string."""

    def __str__(self):
        return str(self.name)


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
    """Azure HTTP authorization level, Determines what keys, if any, need to
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


class HttpMethod(StringifyEnum):
    """All http methods Azure Python function supports."""
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    HEAD = "HEAD"
    PATCH = "PATCH"
    PUT = "PUT"
    OPTIONS = "OPTIONS"


# Binding types
class Binding(ABC):
    @staticmethod
    @abstractmethod
    def get_binding_name() -> str:
        pass

    def __init__(self, name: str,
                 direction: BindingDirection,
                 data_type: DataType,
                 is_trigger: bool):
        self._type = self.get_binding_name()
        self.is_trigger = is_trigger
        self._name = name
        self._direction = direction
        self._data_type = data_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def data_type(self) -> int:
        return self._data_type.value

    @property
    def direction(self) -> int:
        return self._direction.value

    @abstractmethod
    def get_dict_repr(self) -> Dict:
        pass

    def __str__(self) -> str:
        return str(self.get_dict_repr())


class Trigger(Binding, metaclass=ABCMeta):
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, is_trigger=True)


class InputBinding(Binding, metaclass=ABCMeta):
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, is_trigger=False)


class OutputBinding(Binding, metaclass=ABCMeta):
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.OUT,
                         name=name, data_type=data_type, is_trigger=False)
