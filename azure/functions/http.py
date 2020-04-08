import json
import typing

from azure.functions import _abc as azf_abc
from azure.functions import _http as azf_http

from . import meta


class HttpRequest(azf_http.HttpRequest):
    """An HTTP request object."""

    __body_bytes: typing.Optional[bytes]
    __body_str: typing.Optional[str]

    def __init__(self,
                 method: str,
                 url: str, *,
                 headers: typing.Mapping[str, str],
                 params: typing.Mapping[str, str],
                 route_params: typing.Mapping[str, str],
                 body_type: str,
                 body: typing.Union[str, bytes]) -> None:

        body_str: typing.Optional[str] = None
        body_bytes: typing.Optional[bytes] = None
        if isinstance(body, str):
            body_str = body
            body_bytes = body_str.encode('utf-8')
        elif isinstance(body, bytes):
            body_bytes = body
        else:
            raise TypeError(
                f'unexpected HTTP request body type: {type(body).__name__}')

        super().__init__(method=method, url=url, headers=headers,
                         params=params, route_params=route_params,
                         body=body_bytes)

        self.__body_type = body_type
        self.__body_str = body_str
        self.__body_bytes = body_bytes

    def get_body(self) -> bytes:
        if self.__body_bytes is None:
            assert self.__body_str is not None
            self.__body_bytes = self.__body_str.encode('utf-8')
        return self.__body_bytes

    def get_json(self) -> typing.Any:
        if self.__body_type in ('json', 'string'):
            assert self.__body_str is not None
            return json.loads(self.__body_str)
        elif self.__body_bytes is not None:
            try:
                return json.loads(self.__body_bytes.decode())
            except ValueError as e:
                raise ValueError(
                    'HTTP request does not contain valid JSON data') from e
        else:
            raise ValueError(
                'Request body cannot be empty in JSON deserialization')


class HttpResponseConverter(meta.OutConverter, binding='http'):

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (azf_abc.HttpResponse, str))

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        if isinstance(obj, azf_abc.HttpResponse):
            status = obj.status_code
            headers = dict(obj.headers)
            if 'content-type' not in headers:
                if obj.mimetype.startswith('text/'):
                    ct = f'{obj.mimetype}; charset={obj.charset}'
                else:
                    ct = f'{obj.mimetype}'
                headers['content-type'] = ct

            body = obj.get_body()
            if body is not None:
                datum_body = meta.Datum(type='bytes', value=body)
            else:
                datum_body = meta.Datum(type='bytes', value=b'')

            return meta.Datum(
                type='http',
                value=dict(
                    status_code=meta.Datum(type='string', value=str(status)),
                    headers={
                        n: meta.Datum(type='string', value=h)
                        for n, h in headers.items()
                    },
                    body=datum_body,
                )
            )

        raise NotImplementedError


class HttpRequestConverter(meta.InConverter,
                           binding='httpTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, azf_abc.HttpRequest)

    @classmethod
    def decode(cls, data: meta.Datum, *,
               trigger_metadata) -> typing.Any:
        if data.type != 'http':
            raise NotImplementedError

        val = data.value

        return HttpRequest(
            method=val['method'].value,
            url=val['url'].value,
            headers={n: v.value for n, v in val['headers'].items()},
            params={n: v.value for n, v in val['query'].items()},
            route_params={n: v.value for n, v in val['params'].items()},
            body_type=val['body'].type,
            body=val['body'].value,
        )
