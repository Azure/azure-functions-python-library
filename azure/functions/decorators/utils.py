#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from enum import Enum
from json import JSONEncoder
from typing import TypeVar, Optional, Union, Iterable, Type

from azure.functions.decorators.core import StringifyEnum

T = TypeVar("T", bound=Enum)


def parse_singular_param(param: Optional[Union[T, str]],
                         class_name: Type[T]) -> Optional[T]:
    if param is None:
        return None
    if isinstance(param, str):
        return class_name[param]

    return param


def parse_iterable_param(
        param_values: Optional[Union[Iterable[str], Iterable[T]]],
        class_name: Type[T]) -> Optional[Iterable[T]]:
    if param_values is None:
        return None

    return [class_name[value] if isinstance(value, str) else value for value in
            param_values]


class EnumEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, StringifyEnum):
            return str(o)

        return super().default(o)


enum_encoder = EnumEncoder()
# print(isinstance(HttpMethod.HEAD, Enum))
# print(parse_param('GET', HttpMethod))
# print(type(parse_param('GET', HttpMethod)))
# print(parse_iterable_param(['GET', 'POST'], HttpMethod))
# print(type(parse_iterable_param(['GET', 'POST'], HttpMethod)))
