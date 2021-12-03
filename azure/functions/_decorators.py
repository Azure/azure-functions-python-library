# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from typing import Dict, List, Union


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
                 data_type: DataType = DataType.UNDEFINED):
        self.direction: int = direction.value
        self.type: str = self.get_binding_name()
        self.data_type: int = data_type.value
        self.name: str = name

    @abstractmethod
    def get_dict_repr(self):
        pass

    def get_binding_direction(self) -> str:
        return str(self.direction)

    def __str__(self) -> str:
        return str(self.get_dict_repr())


class Trigger(Binding, metaclass=ABCMeta):
    def __init__(self, name) -> None:
        self.is_trigger = True
        super().__init__(direction=BindingDirection.IN,
                         name=name)


class InputBinding(Binding, metaclass=ABCMeta):
    def __init__(self, name) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name)


class OutputBinding(Binding, metaclass=ABCMeta):
    def __init__(self, name) -> None:
        super().__init__(direction=BindingDirection.OUT,
                         name=name)


class DummyTrigger(Trigger):
    @staticmethod
    def get_binding_name(Scaffold) -> str:
        return "Dummy"

    def get_dict_repr(self) -> Dict[str, str]:
        return {"dummy": "trigger"}

    def __init__(self):
        super(DummyTrigger, self).__init__(name="Dummy")


class Scaffold(ABC):
    def __init__(self, app_script_file="app_file"):
        self.app_script_file = app_script_file

    @abstractmethod
    def on_trigger(self, trigger: Trigger, function_name: str, *args, **kwargs):
        pass

    @abstractmethod
    def binding(self, binding: Binding, *args, **kwargs):
        pass
