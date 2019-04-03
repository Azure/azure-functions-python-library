import unittest

import azure.functions as func


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
