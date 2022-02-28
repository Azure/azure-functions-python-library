# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
from abc import ABC, abstractmethod
from typing import Dict, Optional

from azure.functions.decorators.utils import CustomJsonEncoder, camel_case, \
    ABCBuildDictMeta, StringifyEnum

# script file name
SCRIPT_FILE_NAME = "function_app.py"


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
    """Abstract binding class which captures common attributes and
    functions. :meth:`get_dict_repr` can auto generate the function.json for
    every binding, the only restriction is ***ENSURE*** __init__ parameter
    names of any binding class are snake case form of corresponding
    attribute in function.json when new binding classes are created.
    Ref: https://aka.ms/azure-function-binding-http """

    @staticmethod
    @abstractmethod
    def get_binding_name() -> str:
        pass

    def __init__(self, name: str,
                 direction: BindingDirection,
                 is_trigger: bool,
                 data_type: Optional[DataType] = None):
        self.type = self.get_binding_name()
        self.is_trigger = is_trigger
        self.name = name
        self._direction = direction
        self._data_type = data_type
        self._dict = {
            "direction": self._direction,
            "dataType": self._data_type,
            "type": self.type
        }

    @property
    def data_type(self) -> Optional[int]:
        return self._data_type.value if self._data_type else None

    @property
    def direction(self) -> int:
        return self._direction.value

    def get_dict_repr(self) -> Dict:
        """Build a dictionary of a particular binding. The keys are camel
        cased binding field names defined in `init_params` list and
        :class:`Binding` class.

        :return: Dictionary representation of the binding.
        """
        for p in getattr(self, 'init_params', []):
            if p not in ['data_type', 'self']:
                self._dict[camel_case(p)] = getattr(self, p, None)

        return self._dict

    def get_binding_json(self) -> str:
        return json.dumps(self.get_dict_repr(), cls=CustomJsonEncoder)

    def __str__(self):
        return self.get_binding_json()


class Trigger(Binding, ABC, metaclass=ABCBuildDictMeta):
    """Class representation of Azure Function Trigger. \n
    Ref: https://aka.ms/functions-triggers-bindings-overview
    """
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, is_trigger=True)


class InputBinding(Binding, ABC, metaclass=ABCBuildDictMeta):
    """Class representation of Azure Function Input Binding. \n
    Ref: https://aka.ms/functions-triggers-bindings-overview
    """
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, is_trigger=False)


class OutputBinding(Binding, ABC, metaclass=ABCBuildDictMeta):
    """Class representation of Azure Function Output Binding. \n
    Ref: https://aka.ms/functions-triggers-bindings-overview
    """
    def __init__(self, name, data_type) -> None:
        super().__init__(direction=BindingDirection.OUT,
                         name=name, data_type=data_type, is_trigger=False)
