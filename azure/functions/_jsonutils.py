# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from abc import ABC, abstractmethod
from typing import Any, Union
from types import SimpleNamespace


"""
Azure Functions JSON utilities.
This module provides a JSON interface that can be used to serialize and
deserialize objects to and from JSON format. It supports both the `orjson`
and the standard `json` libraries, falling back to the standard library
if `orjson` is not available (installed).
"""


class JsonInterface(ABC):
    @abstractmethod
    def dumps(self, obj: Any, **kwargs: Any) -> str:
        pass

    @abstractmethod
    def loads(self, s: Union[str, bytes, bytearray]) -> Any:
        pass


class OrJsonAdapter(JsonInterface):
    def __init__(self):
        import orjson
        self.orjson = orjson

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        if kwargs:
            # orjson doesn't support keyword arguments
            import json
            return json.dumps(obj, **kwargs)
            
        # orjson.dumps returns bytes, decode to str
        return self.orjson.dumps(obj).decode("utf-8")

    def loads(self, s: Union[str, bytes, bytearray]) -> Any:
        return self.orjson.loads(s)


class StdJsonAdapter(JsonInterface):
    def __init__(self):
        import json
        self.json = json

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        return self.json.dumps(obj, **kwargs)

    def loads(self, s: Union[str, bytes, bytearray]) -> Any:
        return self.json.loads(s)


try:
    json_impl: JsonInterface = OrJsonAdapter()
except ImportError:
    json_impl = StdJsonAdapter()


def dumps(obj, **kwargs) -> str:
    return json_impl.dumps(obj, **kwargs)


def loads(s: Union[str, bytes, bytearray]) -> Any:
    return json_impl.loads(s)


json = SimpleNamespace(
    dumps=dumps,
    loads=loads
)
