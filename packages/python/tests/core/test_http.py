import unittest
from unittest.mock import patch
from m.core.http import fetch


class HttpTest(unittest.TestCase):

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_http(self, MockResponse, MockHttp, MockHttps):
        inst = MockResponse.return_value
        http_inst = MockHttp.return_value
        http_inst.getresponse.return_value = inst
        inst.getcode.return_value = 200
        result = fetch('http://google.com', {})
        MockHttp.assert_called_once_with('google.com')
        MockHttps.assert_not_called()
        # MockHttp.request.assert_called()

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_https(self, MockResponse, MockHttp, MockHttps):
        inst = MockResponse.return_value
        http_inst = MockHttps.return_value
        http_inst.getresponse.return_value = inst
        inst.getcode.return_value = 200
        result = fetch('https://google.com', {})
        MockHttps.assert_called_once_with('google.com')
        MockHttp.assert_not_called()
        # MockHttp.request.assert_called()

    @patch('http.client.HTTPSConnection')
    @patch('http.client.HTTPConnection')
    @patch('http.client.HTTPResponse')
    def test_fetch_ex(self, MockResponse, MockHttp, MockHttps):
        inst = MockResponse.return_value
        http_inst = MockHttps.return_value
        http_inst.getresponse.side_effect = Exception('oops')
        result = fetch('https://google.com', {})
        print(result.value)
        # MockHttp.request.assert_called()


