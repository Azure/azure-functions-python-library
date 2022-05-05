# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import sys
import unittest
from unittest import skipIf

import azure.functions as func
import azure.functions.http as http
from azure.functions._http import HttpResponseHeaders


class TestHTTP(unittest.TestCase):
    def test_http_form_parse_files(self):
        data = (
            b"--foo\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Content-Disposition: form-data; name=rfc2231;\r\n"
            b"  filename*0*=ascii''a%20b%20;\r\n"
            b"  filename*1*=c%20d%20;\r\n"
            b'  filename*2="e f.txt"\r\n\r\n'
            b"file contents\r\n--foo--"
        )
        request = func.HttpRequest(
            method='POST',
            url='/foo',
            body=data,
            headers={
                'Content-Type': 'multipart/form-data; boundary=foo'
            }
        )

        self.assertEqual(request.files["rfc2231"].filename, "a b c d e f.txt")
        self.assertEqual(request.files["rfc2231"].read(), b"file contents")

    def test_http_json(self):
        data: bytes = b'{ "result": "OK" }'
        request = func.HttpRequest(
            method='POST',
            url='/foo',
            body=data,
            headers={
                'Content-Type': 'application/json; charset=utf-8'
            }
        )

        self.assertEqual(request.get_body(), b'{ "result": "OK" }')
        self.assertEqual(request.get_json().get('result'), 'OK')

    def test_http_form_parse_urlencoded(self):
        data = b"foo=Hello+World&bar=baz"
        req = func.HttpRequest(
            method="POST",
            url='/foo',
            body=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
        )
        self.assertEqual(req.form["foo"], u"Hello World")

    def test_http_form_parse_formdata(self):
        data = (
            b"--foo\r\nContent-Disposition: form-field; name=foo\r\n\r\n"
            b"Hello World\r\n"
            b"--foo\r\nContent-Disposition: form-field; name=bar\r\n\r\n"
            b"bar=baz\r\n--foo--"
        )
        req = func.HttpRequest(
            method="POST",
            url='/foo',
            body=data,
            headers={
                'Content-Type': 'multipart/form-data; boundary=foo'
            },
        )
        self.assertEqual(req.form["foo"], u"Hello World")
        self.assertEqual(req.form["bar"], u"bar=baz")

    def test_http_input_type(self):
        check_input_type = (
            http.HttpRequestConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(func.HttpRequest))
        self.assertFalse(check_input_type(str))

    def test_http_output_type(self):
        check_output_type = (
            http.HttpResponseConverter.check_output_type_annotation
        )
        self.assertTrue(check_output_type(func.HttpResponse))
        self.assertTrue(check_output_type(str))

    def test_http_response_encode_to_datum_no_cookie(self):
        resp = func.HttpResponse()
        datum = http.HttpResponseConverter.encode(resp, expected_type=None)

        self.assertEqual(datum.value["cookies"], None)

    @skipIf(sys.version_info < (3, 8, 0),
            "Skip the tests for Python 3.7 and below")
    def test_http_response_encode_to_datum_with_cookies(self):
        headers = HttpResponseHeaders()
        headers.add("Set-Cookie",
                    'foo3=42; Domain=example.com; Expires=Thu, '
                    '12-Jan-2017 13:55:08 GMT; Path=/; Max-Age=10000000')
        headers.add("Set-Cookie",
                    'foo3=43; Domain=example.com; Expires=Thu, 12-Jan-2018 '
                    '13:55:09 GMT; Path=/; Max-Age=10000000')
        resp = func.HttpResponse(headers=headers)
        datum = http.HttpResponseConverter.encode(resp, expected_type=None)

        actual_cookies = datum.value['cookies']
        self.assertIsNotNone(actual_cookies)
        self.assertTrue(isinstance(actual_cookies, list))
        self.assertTrue(len(actual_cookies), 2)
        self.assertEqual(str(actual_cookies[0]),
                         "Set-Cookie: foo3=42; Domain=example.com; "
                         "expires=Thu, 12-Jan-2017 13:55:08 GMT; "
                         "Max-Age=10000000; Path=/")
        self.assertEqual(str(actual_cookies[1]),
                         "Set-Cookie: foo3=43; Domain=example.com; "
                         "expires=Thu, 12-Jan-2018 13:55:09 GMT; "
                         "Max-Age=10000000; Path=/")

        self.assertTrue("Set-Cookie" not in resp.headers)

    @skipIf(sys.version_info >= (3, 8, 0),
            "Skip the tests for Python 3.8 and above")
    def test_http_response_encode_to_datum_with_cookies_in_python_3_7(self):
        headers = HttpResponseHeaders()
        headers.add("Set-Cookie",
                    'foo3=42; Domain=example.com; Expires=Thu, '
                    '12-Jan-2017 13:55:08 GMT; Path=/; Max-Age=10000000')
        headers.add("Set-Cookie",
                    'foo3=43; Domain=example.com; Expires=Thu, 12-Jan-2018 '
                    '13:55:09 GMT; Path=/; Max-Age=10000000')
        resp = func.HttpResponse(headers=headers)
        datum = http.HttpResponseConverter.encode(resp, expected_type=None)

        actual_cookies = datum.value['cookies']
        self.assertIsNone(actual_cookies)
        self.assertIn("Set-Cookie", resp.headers,
                      "Set-Cookie header not present in response headers!")

    @skipIf(sys.version_info < (3, 8, 0),
            "Skip the tests for Python 3.7 and below")
    def test_http_response_encode_to_datum_with_cookies_lower_case(self):
        headers = HttpResponseHeaders()
        headers.add("set-cookie",
                    'foo3=42; Domain=example.com; Path=/; Max-Age=10000.0')
        resp = func.HttpResponse(headers=headers)
        datum = http.HttpResponseConverter.encode(resp, expected_type=None)

        actual_cookies = datum.value['cookies']
        self.assertIsNotNone(actual_cookies)
        self.assertTrue(isinstance(actual_cookies, list))
        self.assertTrue(len(actual_cookies), 1)
        self.assertEqual(str(actual_cookies[0]),
                         "Set-Cookie: foo3=42; Domain=example.com; "
                         "Max-Age=10000.0; Path=/")

    def test_http_request_should_not_have_implicit_output(self):
        self.assertFalse(http.HttpRequestConverter.has_implicit_output())

    def test_http_response_does_not_have_explicit_output(self):
        self.assertIsNone(
            getattr(http.HttpResponseConverter, 'has_implicit_output', None)
        )
