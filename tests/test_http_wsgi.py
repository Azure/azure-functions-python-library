# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import threading
import unittest
from io import StringIO, BytesIO

import pytest

import azure.functions as func
from azure.functions._abc import TraceContext, RetryContext
from azure.functions._http import HttpResponseHeaders
from azure.functions._http_wsgi import (
    WsgiRequest,
    WsgiResponse,
    WsgiMiddleware
)
from azure.functions._http_asgi import AsgiRequest


class WsgiException(Exception):
    def __init__(self, message=''):
        self.message = message


class TestHttpWsgi(unittest.TestCase):

    def test_request_general_environ_conversion(self):
        func_request = self._generate_func_request()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertEqual(environ['REQUEST_METHOD'], 'POST')
        self.assertEqual(environ['SCRIPT_NAME'], '')
        self.assertEqual(environ['PATH_INFO'], '/api/http')
        self.assertEqual(environ['QUERY_STRING'], 'firstname=rt')
        self.assertEqual(environ['CONTENT_TYPE'], 'application/json')
        self.assertEqual(environ['CONTENT_LENGTH'],
                         str(len(b'{ "lastname": "tsang" }')))
        self.assertEqual(environ['SERVER_NAME'], 'function.azurewebsites.net')
        self.assertEqual(environ['SERVER_PORT'], '443')
        self.assertEqual(environ['SERVER_PROTOCOL'], 'HTTP/1.1')

    def test_request_wsgi_environ_conversion(self):
        func_request = self._generate_func_request()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertEqual(environ['wsgi.version'], (1, 0))
        self.assertEqual(environ['wsgi.url_scheme'], 'https')

        self.assertIsInstance(environ['wsgi.input'], BytesIO)
        bytes_io: BytesIO = environ['wsgi.input']
        bytes_io.seek(0)
        self.assertEqual(bytes_io.read(), b'{ "lastname": "tsang" }')

        self.assertIsInstance(environ['wsgi.errors'], StringIO)
        string_io: StringIO = environ['wsgi.errors']
        string_io.seek(0)
        self.assertEqual(string_io.read(), '')

        self.assertEqual(environ['wsgi.multithread'], False)
        self.assertEqual(environ['wsgi.multiprocess'], False)
        self.assertEqual(environ['wsgi.run_once'], False)

    def test_request_http_environ_conversion(self):
        func_request = self._generate_func_request()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertEqual(environ['HTTP_X_MS_SITE_RESTRICTED_TOKEN'], 'xmsrt')

    def test_request_has_no_query_param(self):
        func_request = self._generate_func_request(
            url="https://function.azurewebsites.net",
            params=None)
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertEqual(environ['QUERY_STRING'], '')

    def test_request_has_no_body(self):
        func_request = self._generate_func_request(body=None)
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertEqual(environ['CONTENT_LENGTH'], str(0))

        self.assertIsInstance(environ['wsgi.input'], BytesIO)
        bytes_io: BytesIO = environ['wsgi.input']
        bytes_io.seek(0)
        self.assertEqual(bytes_io.read(), b'')

    def test_request_has_no_headers(self):
        func_request = self._generate_func_request(headers=None)
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertNotIn('CONTENT_TYPE', environ)

    def test_request_protocol_by_header(self):
        func_request = self._generate_func_request(headers={
            "x-forwarded-port": "8081"
        })
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertEqual(environ['SERVER_PORT'], str(8081))
        self.assertEqual(environ['wsgi.url_scheme'], 'https')

    def test_request_protocol_by_scheme(self):
        func_request = self._generate_func_request(url="http://a.b.com")
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)
        self.assertEqual(environ['SERVER_PORT'], str(80))
        self.assertEqual(environ['wsgi.url_scheme'], 'http')

    def test_request_parse_function_context(self):
        func_request = self._generate_func_request()
        func_context = self._generate_func_context()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request,
                              func_context).to_environ(error_buffer)
        self.assertEqual(environ['azure_functions.invocation_id'],
                         '123e4567-e89b-12d3-a456-426655440000'),
        self.assertIsNotNone(environ['azure_functions.thread_local_storage'])
        self.assertEqual(environ['azure_functions.function_name'],
                         'httptrigger')
        self.assertEqual(environ['azure_functions.function_directory'],
                         '/home/roger/wwwroot/httptrigger')
        self.assertEqual(environ['azure_functions.trace_context'],
                         TraceContext)
        self.assertEqual(environ['azure_functions.retry_context'],
                         RetryContext)

    def test_response_from_wsgi_app(self):
        app = self._generate_wsgi_app()
        func_request = self._generate_func_request()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)

        wsgi_response: WsgiResponse = WsgiResponse.from_app(app, environ)
        func_response: func.HttpResponse = wsgi_response.to_func_response()

        self.assertEqual(func_response.mimetype, 'text/plain')
        self.assertEqual(func_response.charset, 'utf-8')
        self.assertEqual(func_response.headers['Content-Type'], 'text/plain')
        self.assertEqual(func_response.status_code, 200)
        self.assertEqual(func_response.get_body(), b'sample string')

    def test_response_no_body(self):
        app = self._generate_wsgi_app(response_body=None)
        func_request = self._generate_func_request()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)

        wsgi_response: WsgiResponse = WsgiResponse.from_app(app, environ)
        func_response: func.HttpResponse = wsgi_response.to_func_response()
        self.assertEqual(func_response.get_body(), b'')

    def test_response_no_headers(self):
        app = self._generate_wsgi_app(response_headers=None)
        func_request = self._generate_func_request()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)

        wsgi_response: WsgiResponse = WsgiResponse.from_app(app, environ)
        func_response: func.HttpResponse = wsgi_response.to_func_response()
        self.assertEqual(func_response.headers, HttpResponseHeaders([]))

    def test_response_with_exception(self):
        app = self._generate_wsgi_app(
            exception=WsgiException(message='wsgi excpt'))
        func_request = self._generate_func_request()
        error_buffer = StringIO()
        environ = WsgiRequest(func_request).to_environ(error_buffer)

        with self.assertRaises(WsgiException) as e:
            wsgi_response = WsgiResponse.from_app(app, environ)
            wsgi_response.to_func_response()

        self.assertEqual(e.exception.message, 'wsgi excpt')

    def test_middleware_handle(self):
        """Test if the middleware can be used by exposing the .handle method,
        specifically when the middleware is used as
        def main(req, context):
            return WsgiMiddleware(app).handle(req, context)
        """
        app = self._generate_wsgi_app()
        func_request = self._generate_func_request()
        func_response = WsgiMiddleware(app).handle(func_request)
        self.assertEqual(func_response.status_code, 200)
        self.assertEqual(func_response.get_body(), b'sample string')

    def test_middleware_handle_with_server_error_status_code(self):
        """Test if the middleware can be used by exposing the .handle method,
        specifically when the middleware is used as
        def main(req, context):
            return WsgiMiddleware(app).handle(req, context)
        """
        app = self._generate_wsgi_app(status="500 Internal Server Error",
                                      response_body=b'internal server error')
        func_request = self._generate_func_request()
        with pytest.raises(Exception) as exec_info:
            func_response = WsgiMiddleware(app).handle(func_request)
            self.assertEqual(func_response.status_code, 500)
        self.assertEqual(exec_info.value.args[0], b'internal server error')

    def test_middleware_wrapper(self):
        """Test if the middleware can be used by exposing the .main property,
        specifically when the middleware is used as
        main = WsgiMiddleware(app).main
        """
        app = self._generate_wsgi_app()
        main = WsgiMiddleware(app).main
        func_request = self._generate_func_request()
        func_context = self._generate_func_context()
        func_response = main(func_request, func_context)
        self.assertEqual(func_response.status_code, 200)
        self.assertEqual(func_response.get_body(), b'sample string')

    def test_path_encoding_utf8(self):
        url = 'http://example.com/Pippi%20L%C3%A5ngstrump'
        request = AsgiRequest(self._generate_func_request(url=url))

        self.assertEqual(request.path_info, u'/Pippi L\u00e5ngstrump')

    def test_path_encoding_latin1(self):
        url = 'http://example.com/Pippi%20L%C3%A5ngstrump'
        request = WsgiRequest(self._generate_func_request(url=url))

        self.assertEqual(request.path_info, u'/Pippi L\u00c3\u00a5ngstrump')

    def _generate_func_request(
            self,
            method="POST",
            url="https://function.azurewebsites.net/api/http?firstname=rt",
            headers={
                "Content-Type": "application/json",
                "x-ms-site-restricted-token": "xmsrt"
            },
            params={
                "firstname": "roger"
            },
            route_params={},
            body=b'{ "lastname": "tsang" }'
    ) -> func.HttpRequest:
        return func.HttpRequest(
            method=method,
            url=url,
            headers=headers,
            params=params,
            route_params=route_params,
            body=body
        )

    def _generate_func_context(
        self,
        invocation_id='123e4567-e89b-12d3-a456-426655440000',
        thread_local_storage=threading.local(),
        function_name='httptrigger',
        function_directory='/home/roger/wwwroot/httptrigger',
        trace_context=TraceContext,
        retry_context=RetryContext
    ) -> func.Context:
        class MockContext(func.Context):
            def __init__(self, ii, tls, fn, fd, tc, rc):
                self._invocation_id = ii
                self._thread_local_storage = tls
                self._function_name = fn
                self._function_directory = fd
                self._trace_context = tc
                self._retry_context = rc

            @property
            def invocation_id(self):
                return self._invocation_id

            @property
            def thread_local_storage(self):
                return self._thread_local_storage

            @property
            def function_name(self):
                return self._function_name

            @property
            def function_directory(self):
                return self._function_directory

            @property
            def trace_context(self):
                return self._trace_context

            @property
            def retry_context(self):
                return self._retry_context

        return MockContext(invocation_id, thread_local_storage,
                           function_name, function_directory,
                           trace_context, retry_context)

    def _generate_wsgi_app(self,
                           status='200 OK',
                           response_headers=[('Content-Type', 'text/plain')],
                           response_body=b'sample string',
                           exception: WsgiException = None):
        class MockWsgiApp:
            _status = status
            _response_headers = response_headers
            _response_body = response_body
            _exception = exception

            def __init__(self, environ, start_response):
                self._environ = environ
                self._start_response = start_response

            def __iter__(self):
                if self._exception is not None:
                    raise self._exception

                self._start_response(self._status, self._response_headers)
                yield self._response_body

        return MockWsgiApp
