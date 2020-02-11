from typing import Callable, Dict
from urllib.parse import urlparse

from ._abc import Context
from ._http import HttpRequest, HttpResponse


class WsgiRequest:
    def __init__(self, func_req: HttpRequest):
        url = urlparse(func_req.url)

        # Convert function request headers to lowercase header
        self._lowercased_headers = {
            k.lower():v for k,v in func_req.headers.items()
        }

        # Implement interfaces for PEP 3333 environ
        self.request_method = func_req.method
        self.script_name = ''
        self.path_info = url.path
        self.query_string = url.query
        self.content_type = self._lowercased_headers.get('content-type')
        self.content_length = self._lowercased_headers.get('content-length')
        self.server_name = url.hostname
        self.server_port = self._get_port(url, self._lowercased_headers)
        self.server_protocol = 'HTTP/1.1'

        # Pass http headers Content-Type
        self._http_environ: Dict[str, str] = self._get_http_headers(func_req.headers)


    
    def _get_port(parsed_url, lowercased_headers: Dict[str, str]) -> int:
        port: int = 80
        if lowercased_headers.get('x-forwarded-port'):
            return int(lowercased_headers['x-forwarded-port'])
        elif getattr(parsed_url, 'port', None):
            return parsed_url.port
        elif parsed_url.scheme == 'https':
            return 443
        return port

    def _get_http_headers(func_headers: Dict[str, str]) -> Dict[str, str]:
        # Content-Type -> HTTP_CONTENT_TYPE
        return {
            f'HTTP_{k.upper().}':v for k,v in func_headers.items()
        }

class WsgiMiddleware:
    def __init__(self, app):
        self._app = app

    @property
    def main(self) -> Callable[[HttpRequest, Context], HttpResponse]:
        return WsgiMiddleware.handle

    def handle(cls, req: HttpRequest, context: Context = None) -> HttpResponse:
        req_url = req.url
        req_body = req.get_body()
        req_headers = req.headers

        environ = {}
        self._inject_general_environ(environ)
        self._inject_http_environ(environ)
        self._inject_wsgi_environ(environ)

    def _inject_general_environ(env: Dict[str, str], req_body: bytes, req_headers: Dict[str, str]):
        env.update({
            'CONTENT_LENGTH': req_headers.get('Content-Length'),
            'CONTENT_TYPE': req_headers.get('Content-Type'),
            'PATH_INFO': url_unquote(path_info),
            'QUERY_STRING': encode_query_string(event),
            'REMOTE_ADDR': event[u'requestContext']
            .get(u'identity', {})
            .get(u'sourceIp', ''),
            'REMOTE_USER': event[u'requestContext']
            .get(u'authorizer', {})
            .get(u'principalId', ''),
            'REQUEST_METHOD': event[u'httpMethod'],
            'SCRIPT_NAME': script_name,
            'SERVER_NAME': headers.get(u'Host', 'lambda'),
            'SERVER_PORT': headers.get(u'X-Forwarded-Port', '80'),
            'SERVER_PROTOCOL': 'HTTP/1.1',
        })

    def _inject_http_environ(env: Dict[str, str]):

    def _inject_wsgi_environ(env: Dict[str, str]):
