from typing import Callable, Dict
from

from ._abc import Context
from ._http import HttpRequest, HttpResponse


class WsgiMiddleware:
    def __init__(self, app):
        self._app = app

    @property
    def main(self) -> Callable[[HttpRequest, Context], HttpResponse]:
        return WsgiMiddleware.handle

    def handle(cls, req: HttpRequest, context: Context = None) -> HttpResponse:
        req_url = req.url
        req_body = req.get_body()

        environ = {}
        self._inject_general_environ(environ)
        self._inject_http_environ(environ)
        self._inject_wsgi_environ(environ)

    def _inject_general_environ(env: Dict[str, str]):
        env.update({
            "CONTENT_TYPE":
        })

    def _inject_http_environ(env: Dict[str, str]):

    def _inject_wsgi_environ(env: Dict[str, str]):
