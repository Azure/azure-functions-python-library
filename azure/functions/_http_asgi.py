# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
from typing import Callable, Dict, List, Tuple, Optional, Any
from io import StringIO
import logging
from os import linesep
from wsgiref.headers import Headers

from ._abc import Context
from ._http import HttpRequest, HttpResponse
from ._http_wsgi import WsgiRequest


class AsgiRequest(WsgiRequest):
    _environ_cache: Optional[Dict[str, Any]] = None

    def __init__(self, func_req: HttpRequest, func_ctx: Optional[Context] = None):
        self.asgi_version = "2.1"
        self.asgi_spec_version = "2.1"
        self._headers = func_req.headers
        super().__init__(func_req, func_ctx)

    def _get_encoded_http_headers(self) -> List[Tuple[bytes, bytes]]:
        return [(k.encode("utf8"), v.encode("utf8")) for k, v in self._headers.items()]

    def to_asgi_http_scope(self):
        return {
            "type": "http",
            "asgi.version": self.asgi_version,
            "asgi.spec_version": self.asgi_spec_version,
            "http_version": "1.1",
            "method": self.request_method,
            "scheme": "https",
            "path": self.path_info,
            "raw_path": self.path_info,
            "query_string": self.query_string,
            "root_path": self.script_name,
            "headers": self._get_encoded_http_headers(),
            "server": (self.server_name, self.server_port),
        }
        # Notes, missing client name, port


class AsgiResponse:
    def __init__(self):
        self._status_code = 0
        self._headers = {}
        self._buffer: List[bytes] = []
        self._request_body = b""

    @classmethod
    async def from_app(cls, app, scope: Dict[str, Any], body: bytes) -> "AsgiResponse":
        res = cls()
        res._request_body = body
        await app(scope, res._receive, res._send)
        return res

    def to_func_response(self) -> HttpResponse:
        lowercased_headers = {k.lower(): v for k, v in self._headers.items()}
        return HttpResponse(
            body=b"".join(self._buffer),
            status_code=self._status_code,
            headers=self._headers,
            mimetype=lowercased_headers.get("content-type"),
            charset=lowercased_headers.get("content-encoding"),
        )

    def _handle_http_response_start(self, message: Dict):
        self._headers = Headers([(k.decode(), v.decode()) for k, v in message["headers"]])  # type: ignore
        self._status_code = message["status"]

    def _handle_http_response_body(self, message: Dict):
        self._buffer.append(message["body"])
        # TODO : Handle more_body flag

    async def _receive(self):
        return {
            "type": "http.request",
            "body": self._request_body,
            "more_body": False,
        }

    async def _send(self, message):
        logging.debug(f"Received {message} from ASGI worker.")
        if message["type"] == "http.response.start":
            self._handle_http_response_start(message)
        elif message["type"] == "http.response.body":
            self._handle_http_response_body(message)
        elif message["type"] == "http.disconnect":
            pass  # Nothing todo here


class AsgiMiddleware:
    def __init__(self, app):
        logging.debug("Instantiating ASGI middleware.")
        self._app = app
        self._asgi_error_buffer = StringIO()
        self.loop = asyncio.new_event_loop()
        logging.debug("asyncio event loop initialized.")

    # Usage
    # main = func.AsgiMiddleware(app).main
    @property
    def main(self) -> Callable[[HttpRequest, Context], HttpResponse]:
        return self._handle

    # Usage
    # return func.AsgiMiddleware(app).handle(req, context)
    def handle(
        self, req: HttpRequest, context: Optional[Context] = None
    ) -> HttpResponse:
        logging.info(f"Handling {req.url} as ASGI request.")
        return self._handle(req, context)

    def _handle(self, req: HttpRequest, context: Optional[Context]) -> HttpResponse:
        asgi_request = AsgiRequest(req, context)
        asyncio.set_event_loop(self.loop)
        scope = asgi_request.to_asgi_http_scope()
        asgi_response = self.loop.run_until_complete(
            AsgiResponse.from_app(self._app, scope, req.get_body())
        )
        self._handle_errors()
        return asgi_response.to_func_response()

    def _handle_errors(self):
        if self._asgi_error_buffer.tell() > 0:
            self._asgi_error_buffer.seek(0)
            error_message = linesep.join(self._asgi_error_buffer.readline())
            raise Exception(error_message)
