# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import threading
import unittest

import azure.functions as func
from azure.functions._abc import TraceContext, RetryContext
from azure.functions._http_asgi import (
    AsgiMiddleware
)
import pytest


class MockAsgiApplication:
    response_code = 200
    response_body = b''
    response_headers = [
        [b"content-type", b"text/plain"],
    ]
    startup_called = False
    shutdown_called = False

    def __init__(self, fail_startup=False, fail_shutdown=False):
        self.fail_startup = fail_startup
        self.fail_shutdown = fail_shutdown

    async def __call__(self, scope, receive, send):
        self.received_scope = scope

        # Verify against ASGI specification
        assert scope['asgi.spec_version'] in ['2.0', '2.1']
        assert isinstance(scope['asgi.spec_version'], str)

        assert scope['asgi.version'] in ['2.0', '2.1', '2.2']
        assert isinstance(scope['asgi.version'], str)

        assert isinstance(scope['type'], str)

        if scope['type'] == 'lifespan':
            self.startup_called = True
            startup_message = await receive()
            assert startup_message['type'] == 'lifespan.startup'
            if self.fail_startup:
                if isinstance(self.fail_startup, str):
                    await send({
                        "type": "lifespan.startup.failed",
                        "message": self.fail_startup})
                else:
                    await send({"type": "lifespan.startup.failed"})
            else:
                await send({"type": "lifespan.startup.complete"})
            shutdown_message = await receive()
            assert shutdown_message['type'] == 'lifespan.shutdown'
            if self.fail_shutdown:
                if isinstance(self.fail_shutdown, str):
                    await send({
                        "type": "lifespan.shutdown.failed",
                        "message": self.fail_shutdown})
                else:
                    await send({"type": "lifespan.shutdown.failed"})
            else:
                await send({"type": "lifespan.shutdown.complete"})

            self.shutdown_called = True

        elif scope['type'] == 'http':
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

            assert scope['client'] is None or hasattr(scope['client'],
                                                      '__iter__')
            if scope['client']:
                assert len(scope['client']) == 2
                assert isinstance(scope['client'][0], str)
                assert isinstance(scope['client'][1], int)

            assert scope['server'] is None or hasattr(scope['server'],
                                                      '__iter__')
            if scope['server']:
                assert len(scope['server']) == 2
                assert isinstance(scope['server'][0], str)
                assert isinstance(scope['server'][1], int)

            self.received_request = await receive()
            assert self.received_request['type'] == 'http.request'
            assert isinstance(self.received_request['body'], bytes)
            assert isinstance(self.received_request['more_body'], bool)

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

            self.next_request = await receive()
            assert self.next_request['type'] == 'http.disconnect'
        else:
            raise AssertionError(f"unexpected type {scope['type']}")


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

        return MockContext(invocation_id, thread_local_storage, function_name,
                           function_directory, trace_context, retry_context)

    def test_middleware_calls_app(self):
        app = MockAsgiApplication()
        test_body = b'Hello world!'
        app.response_body = test_body
        app.response_code = 200
        req = self._generate_func_request()
        response = AsgiMiddleware(app).handle(req)

        # Verify asserted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), test_body)

    def test_middleware_calls_app_http(self):
        app = MockAsgiApplication()
        test_body = b'Hello world!'
        app.response_body = test_body
        app.response_code = 200
        req = self._generate_func_request(url="http://a.b.com")
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

    def test_middleware_async_calls_app_with_context(self):
        """Test the middleware with the awaitable handle_async() method
        async def main(req, context):
            return await AsgiMiddleware(app).handle_async(req, context)
        """
        app = MockAsgiApplication()
        test_body = b'Hello world!'
        app.response_body = test_body
        app.response_code = 200
        req = self._generate_func_request()
        ctx = self._generate_func_context()

        async def run_test():
            return await AsgiMiddleware(app).handle_async(req, ctx)

        response = asyncio.run(run_test())

        # Verify asserted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), test_body)

    def test_function_app_lifecycle_events(self):
        mock_app = MockAsgiApplication()
        middleware = AsgiMiddleware(mock_app)

        async def run_test():
            await middleware.notify_startup()
            assert mock_app.startup_called

            await middleware.notify_shutdown()
            assert mock_app.shutdown_called

        asyncio.run(run_test())

    def test_function_app_lifecycle_events_with_failures(self):
        apps = [
            MockAsgiApplication(False, True),
            MockAsgiApplication(True, False),
            MockAsgiApplication(True, True),
            MockAsgiApplication("bork", False),
            MockAsgiApplication(False, "bork"),
            MockAsgiApplication("bork", "bork"),
        ]

        async def run_test(mock_app):
            middleware = AsgiMiddleware(mock_app)
            await middleware.notify_startup()
            assert mock_app.startup_called

            await middleware.notify_shutdown()
            assert mock_app.shutdown_called

        for mock_app in apps:
            asyncio.run(run_test(mock_app))

    def test_calling_shutdown_without_startup_errors(self):
        mock_app = MockAsgiApplication()
        middleware = AsgiMiddleware(mock_app)

        async def run_test():
            await middleware.notify_shutdown()

        with pytest.raises(RuntimeError):
            asyncio.run(run_test())

    def test_asgi_request_to_http_scope_with_state(self):
        """Test that to_asgi_http_scope() accepts and includes state parameter"""
        req = self._generate_func_request()
        ctx = self._generate_func_context()

        from azure.functions._http_asgi import AsgiRequest
        asgi_request = AsgiRequest(req, ctx)

        # Test with state parameter
        test_state = {"key": "value", "counter": 42}
        scope = asgi_request.to_asgi_http_scope(state=test_state)

        self.assertIn("state", scope)
        self.assertEqual(scope["state"], test_state)
        self.assertEqual(scope["state"]["key"], "value")
        self.assertEqual(scope["state"]["counter"], 42)

    def test_asgi_request_to_http_scope_without_state(self):
        """Test that to_asgi_http_scope() works when state is not provided"""
        req = self._generate_func_request()
        ctx = self._generate_func_context()

        from azure.functions._http_asgi import AsgiRequest
        asgi_request = AsgiRequest(req, ctx)

        # Test without state parameter (should be None)
        scope = asgi_request.to_asgi_http_scope()

        self.assertIn("state", scope)
        self.assertIsNone(scope["state"])

    def test_middleware_state_shared_across_requests(self):
        """Test that middleware state is accessible in the ASGI scope"""
        class StateCapturingApp:
            def __init__(self):
                self.captured_state = None

            async def __call__(self, scope, receive, send):
                if scope['type'] == 'http':
                    self.captured_state = scope.get('state')
                    await send({
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [[b"content-type", b"text/plain"]],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b"OK",
                    })

        app = StateCapturingApp()
        middleware = AsgiMiddleware(app)

        # Set some state on the middleware
        middleware.state["user_id"] = 123
        middleware.state["session"] = "abc-xyz"

        req = self._generate_func_request()
        ctx = self._generate_func_context()

        async def run_test():
            return await middleware.handle_async(req, ctx)

        asyncio.run(run_test())

        # Verify the state was passed to the app
        self.assertIsNotNone(app.captured_state)
        self.assertEqual(app.captured_state["user_id"], 123)
        self.assertEqual(app.captured_state["session"], "abc-xyz")

    def test_middleware_state_is_copied_not_shared(self):
        """Test that middleware state is copied, not shared by reference"""
        class StateMutatingApp:
            def __init__(self):
                self.state_at_call = None

            async def __call__(self, scope, receive, send):
                if scope['type'] == 'http':
                    # Capture the state and mutate it
                    self.state_at_call = scope.get('state')
                    if self.state_at_call is not None:
                        self.state_at_call['mutated'] = True
                        self.state_at_call['counter'] = self.state_at_call.get('counter', 0) + 1

                    await send({
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [[b"content-type", b"text/plain"]],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b"OK",
                    })

        app = StateMutatingApp()
        middleware = AsgiMiddleware(app)

        # Set initial state
        middleware.state["counter"] = 0

        req = self._generate_func_request()
        ctx = self._generate_func_context()

        async def run_test():
            return await middleware.handle_async(req, ctx)

        # Make first request
        asyncio.run(run_test())

        # Verify middleware state wasn't mutated
        self.assertEqual(middleware.state["counter"], 0)
        self.assertNotIn("mutated", middleware.state)

        # Make second request to verify state isn't carried over
        asyncio.run(run_test())
        self.assertEqual(middleware.state["counter"], 0)

    def test_middleware_state_with_nested_objects(self):
        """Test that state with nested objects is properly handled"""
        class NestedStateApp:
            def __init__(self):
                self.captured_state = None

            async def __call__(self, scope, receive, send):
                if scope['type'] == 'http':
                    self.captured_state = scope.get('state')
                    await send({
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [[b"content-type", b"text/plain"]],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b"OK",
                    })

        app = NestedStateApp()
        middleware = AsgiMiddleware(app)

        # Set state with nested objects
        middleware.state["config"] = {
            "database": "mydb",
            "timeout": 30
        }
        middleware.state["features"] = ["feature1", "feature2"]

        req = self._generate_func_request()
        ctx = self._generate_func_context()

        async def run_test():
            return await middleware.handle_async(req, ctx)

        asyncio.run(run_test())

        # Verify nested state is accessible
        self.assertIsNotNone(app.captured_state)
        self.assertIn("config", app.captured_state)
        self.assertEqual(app.captured_state["config"]["database"], "mydb")
        self.assertEqual(app.captured_state["config"]["timeout"], 30)
        self.assertEqual(app.captured_state["features"], ["feature1", "feature2"])

    def test_middleware_state_empty_by_default(self):
        """Test that middleware state is empty dict by default"""
        app = MockAsgiApplication()
        middleware = AsgiMiddleware(app)

        self.assertIsInstance(middleware.state, dict)
        self.assertEqual(len(middleware.state), 0)

    def test_middleware_state_persists_across_calls(self):
        """Test that state on middleware instance persists across multiple calls"""
        class CounterApp:
            call_count = 0

            async def __call__(self, scope, receive, send):
                if scope['type'] == 'http':
                    CounterApp.call_count += 1
                    await send({
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [[b"content-type", b"text/plain"]],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b"OK",
                    })

        app = CounterApp()
        middleware = AsgiMiddleware(app)

        # Set state before first call
        middleware.state["initialized"] = True

        req = self._generate_func_request()
        ctx = self._generate_func_context()

        async def run_test():
            return await middleware.handle_async(req, ctx)

        # First call
        asyncio.run(run_test())
        self.assertTrue(middleware.state["initialized"])

        # Second call - state should still be there
        asyncio.run(run_test())
        self.assertTrue(middleware.state["initialized"])
        self.assertEqual(len(middleware.state), 1)
