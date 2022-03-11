# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

import azure.functions as func
from azure.functions._abc import TraceContext, RetryContext
from azure.functions._http_asgi import (
    AsgiMiddleware
)


class MockAsgiApplication:
    response_code = 200
    response_body = b''
    response_headers = [
        [b"content-type", b"text/plain"],
    ]

    async def __call__(self, scope, receive, send):
        self.received_scope = scope
        # Verify against ASGI specification
        assert scope['type'] == 'http'
        assert isinstance(scope['type'], str)

        assert scope['asgi.spec_version'] in ['2.0', '2.1']
        assert isinstance(scope['asgi.spec_version'], str)

        assert scope['asgi.version'] in ['2.0', '2.1', '2.2']
        assert isinstance(scope['asgi.version'], str)

        assert scope['http_version'] in ['1.0', '1.1', '2']
        assert isinstance(scope['http_version'], str)

        assert scope['method'] in ['POST', 'GET', 'PUT', 'DELETE', 'PATCH']
        assert isinstance(scope['method'], str)

        assert scope['scheme'] in ['http', 'https']
        assert isinstance(scope['scheme'], str)

        assert isinstance(scope['path'], str)
        assert isinstance(scope['raw_path'], bytes)
        assert isinstance(scope['query_string'], bytes)
        assert isinstance(scope['root_path'], str)

        assert hasattr(scope['headers'], '__iter__')
        for k, v in scope['headers']:
            assert isinstance(k, bytes)
            assert isinstance(v, bytes)

        assert scope['client'] is None or hasattr(scope['client'], '__iter__')
        if scope['client']:
            assert len(scope['client']) == 2
            assert isinstance(scope['client'][0], str)
            assert isinstance(scope['client'][1], int)

        assert scope['server'] is None or hasattr(scope['server'], '__iter__')
        if scope['server']:
            assert len(scope['server']) == 2
            assert isinstance(scope['server'][0], str)
            assert isinstance(scope['server'][1], int)

        self.received_request = await receive()
        assert self.received_request['type'] == 'http.request'
        assert isinstance(self.received_request['body'], bytes)
        assert isinstance(self.received_request['more_body'], bool)

        self.next_request = await receive()
        assert self.next_request['type'] == 'http.disconnect'

        await send(
            {
                "type": "http.response.start",
                "status": self.response_code,
                "headers": self.response_headers,
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": self.response_body,
            }
        )


class TestHttpAsgiMiddleware(unittest.TestCase):
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
        function_name='httptrigger',
        function_directory='/home/roger/wwwroot/httptrigger',
        trace_context=TraceContext,
        retry_context=RetryContext
    ) -> func.Context:
        class MockContext(func.Context):
            def __init__(self, ii, fn, fd, tc, rc):
                self._invocation_id = ii
                self._function_name = fn
                self._function_directory = fd
                self._trace_context = tc
                self._retry_context = rc

            @property
            def invocation_id(self):
                return self._invocation_id

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

        return MockContext(invocation_id, function_name, function_directory,
                           trace_context, retry_context)

    def test_middleware_calls_app(self):
        app = MockAsgiApplication()
        test_body = b'Hello world!'
        app.response_body = test_body
        app.response_code = 200
        req = func.HttpRequest(method='get', url='/test', body=b'')
        response = AsgiMiddleware(app).handle(req)

        # Verify asserted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), test_body)

    def test_middleware_calls_app_with_context(self):
        """Test if the middleware can be used by exposing the .handle method,
        specifically when the middleware is used as
        def main(req, context):
            return AsgiMiddleware(app).handle(req, context)
        """
        app = MockAsgiApplication()
        test_body = b'Hello world!'
        app.response_body = test_body
        app.response_code = 200
        req = self._generate_func_request()
        ctx = self._generate_func_context()
        response = AsgiMiddleware(app).handle(req, ctx)

        # Verify asserted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), test_body)

    def test_middleware_wrapper(self):
        """Test if the middleware can be used by exposing the .main property,
        specifically when the middleware is used as
        main = AsgiMiddleware(app).main
        """
        app = MockAsgiApplication()
        test_body = b'Hello world!'
        app.response_body = test_body
        app.response_code = 200
        req = self._generate_func_request()
        ctx = self._generate_func_context()

        main = AsgiMiddleware(app).main
        response = main(req, ctx)

        # Verify asserted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), test_body)
