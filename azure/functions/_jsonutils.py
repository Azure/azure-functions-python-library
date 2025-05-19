from abc import ABC, abstractmethod
import types


class JsonInterface(ABC):
    @abstractmethod
    def dumps(self, obj) -> str:
        pass

    @abstractmethod
    def loads(self, s: str):
        pass


class OrJsonAdapter(JsonInterface):
    def __init__(self):
        import orjson
        self.orjson = orjson

    def dumps(self, obj) -> str:
        return self.orjson.dumps(obj).decode("utf-8")

    def loads(self, s: str):
        return self.orjson.loads(s)


class UJsonAdapter(JsonInterface):
    def __init__(self):
        import ujson
        self.ujson = ujson

    def dumps(self, obj) -> str:
        return self.ujson.dumps(obj)

    def loads(self, s: str):
        return self.ujson.loads(s)


class SimpleJsonAdapter(JsonInterface):
    def __init__(self):
        import simplejson
        self.simplejson = simplejson

    def dumps(self, obj) -> str:
        return self.simplejson.dumps(obj)

    def loads(self, s: str):
        return self.simplejson.loads(s)


class StdJsonAdapter(JsonInterface):
    def __init__(self):
        import json
        self.json = json

    def dumps(self, obj, **kwargs) -> str:
        return self.json.dumps(obj, **kwargs)

    def loads(self, s: str):
        return self.json.loads(s)


json_impl = None
for adapter_cls in (OrJsonAdapter, UJsonAdapter, SimpleJsonAdapter,
                    StdJsonAdapter):
    try:
        json_impl = adapter_cls()
        break
    except ImportError:
        continue


def dumps(obj, **kwargs) -> str:
    if json_impl is None:
        raise ImportError("No JSON adapter found")
    return json_impl.dumps(obj, **kwargs)


def loads(s: str):
    if json_impl is None:
        raise ImportError("No JSON adapter found")
    return json_impl.loads(s)


json = types.SimpleNamespace(
    dumps=dumps,
    loads=loads
)
