from abc import ABC, abstractmethod
import logging
from typing import Any, Union
from types import SimpleNamespace


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
    logging.info("Using orjson as the JSON backend")
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
