from typing import cast
from unittest.mock import patch

from m.core import Issue
from m.core.http import fetch

from ..util import FpTestCase


class HttpTest(FpTestCase):

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_http(self, mock_res, mock_http, mock_https):
        response = mock_res.return_value
        http_inst = mock_http.return_value
        http_inst.getresponse.return_value = response
        response.getcode.return_value = 200
        response.read.return_value = 'content'
        fetch_result = fetch('http://google.com', {})
        mock_http.assert_called_once_with('google.com')
        mock_https.assert_not_called()
        fetch_content = cast(str, self.assert_ok(fetch_result))
        self.assertEqual(fetch_content, 'content')

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_https(self, mock_res, mock_http, mock_https):
        response = mock_res.return_value
        https_inst = mock_https.return_value
        https_inst.getresponse.return_value = response
        response.getcode.return_value = 200
        response.read.return_value = 'content'
        fetch_result = fetch('https://google.com', {})
        mock_https.assert_called_once_with('google.com')
        mock_http.assert_not_called()
        fetch_content = cast(str, self.assert_ok(fetch_result))
        self.assertEqual(fetch_content, 'content')

    @patch('http.client.HTTPSConnection')
    def test_fetch_response_ex(self, mock_https):
        http_inst = mock_https.return_value
        http_inst.getresponse.side_effect = Exception('fail getresponse')
        fetch_result = fetch('https://google.com', {})
        self.assert_issue(fetch_result, 'https response failure')
        ex = cast(Issue, fetch_result.value).cause
        self.assertIsInstance(ex, Exception)
        self.assertEqual(str(ex), 'fail getresponse')

    @patch('http.client.HTTPSConnection')
    def test_fetch_request_ex(self, mock_https):
        http_inst = mock_https.return_value
        http_inst.request.side_effect = Exception('fail request')
        fetch_result = fetch('https://google.com', {})
        self.assert_issue(fetch_result, 'https request failure')
        ex = cast(Issue, fetch_result.value).cause
        self.assertIsInstance(ex, Exception)
        self.assertEqual(str(ex), 'fail request')

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_read_ex(self, mock_res, mock_https):
        response = mock_res.return_value
        https_inst = mock_https.return_value
        https_inst.getresponse.return_value = response
        response.getcode.return_value = 200
        response.read.side_effect = Exception('fail read')
        fetch_result = fetch('https://google.com', {})
        self.assert_issue(fetch_result, 'https read failure')
        ex = cast(Issue, fetch_result.value).cause
        self.assertIsInstance(ex, Exception)
        self.assertEqual(str(ex), 'fail read')

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_https_body(self, mock_res, mock_https):
        response = mock_res.return_value
        https_inst = mock_https.return_value
        https_inst.getresponse.return_value = response
        response.getcode.return_value = 200
        response.read.return_value = 'content'
        fetch_result = fetch('https://google.com', {}, body='{"a":1}')
        mock_https.assert_called_once_with('google.com')
        https_inst.request.assert_called_once_with(
            'GET',
            '',
            '{"a":1}',
            {'user-agent': 'm', 'content-length': '7'},
        )
        self.assert_ok(fetch_result)

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_https_server_err(self, mock_res, mock_http, mock_https):
        response = mock_res.return_value
        https_inst = mock_https.return_value
        https_inst.getresponse.return_value = response
        response.getcode.return_value = 500
        response.read.return_value = 'server error'
        fetch_result = fetch('https://google.com', {})
        mock_https.assert_called_once_with('google.com')
        mock_http.assert_not_called()
        self.assert_issue(fetch_result, 'https request failure (500)')
