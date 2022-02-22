#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from enum import Enum
from json import JSONEncoder
from typing import TypeVar, Optional, Union, Iterable, Type

from azure.functions.decorators.core import StringifyEnum

T = TypeVar("T", bound=Enum)


def parse_singular_param_to_enum(param: Optional[Union[T, str]],
                                 class_name: Type[T]) -> Optional[T]:
    if param is None:
        return None
    if isinstance(param, str):
        return class_name[param]

    return param


def parse_iterable_param_to_enum(
        param_values: Optional[Union[Iterable[str], Iterable[T]]],
        class_name: Type[T]) -> Optional[Iterable[T]]:
    if param_values is None:
        return None

    return [class_name[value] if isinstance(value, str) else value for value in
            param_values]


def camel_case(snake_case: str):
    words = snake_case.split('_')
    return words[0] + ''.join(ele.title() for ele in words[1:])


class CustomJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, StringifyEnum):
            return str(o)

        return super().default(o)
