# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from abc import ABC, ABCMeta, abstractmethod
from enum import Enum


class StringifyEnum(Enum):
    def __str__(self):
        return str(self.name)


class BindingDirection(StringifyEnum):
    IN = 0
    OUT = 1
    INOUT = 2


class DataType(StringifyEnum):
    UNDEFINED = 0
    STRING = 1
    BINARY = 2
    STREAM = 3


class Binding(ABC):
    @staticmethod
    @abstractmethod
    def get_binding_name():
        pass

    def __init__(self, name: str,
                 direction: BindingDirection,
                 data_type: DataType = DataType.UNDEFINED,
                 is_trigger: bool = False):
        self._type = self.get_binding_name()
        self.is_trigger = is_trigger
        self._name = name

        self._direction = direction
        self._data_type = data_type

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def data_type(self):
        return self._data_type.value

    @property
    def direction(self):
        return self._direction.value

    @abstractmethod
    def get_dict_repr(self):
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


class AuthLevel(StringifyEnum):
    FUNCTION = "function"
    ANONYMOUS = "anonymous"
    ADMIN = "admin"
