from typing import cast

import pytest
from m.core import Issue
from m.core.http import fetch
from pytest_mock import MockerFixture
from tests.conftest import assert_issue, assert_ok

HOST = 'hotdog.com'


def mock_http_connection(mocker: MockerFixture):
    """Generate mocks for https, http and response objects.

    Args:
        mocker: A mocker fixture.

    Returns:
        A tuple with https, http, response mocks.
    """
    https_mock = mocker.patch('http.client.HTTPSConnection')
    http_mock = mocker.patch('http.client.HTTPConnection')
    res_mock = mocker.patch('http.client.HTTPResponse')
    return https_mock, http_mock, res_mock


@pytest.mark.parametrize('protocol', ['http', 'https'])
def test_http_vs_https_fetch(mocker: MockerFixture, protocol) -> None:
    https_mock, http_mock, res_mock = mock_http_connection(mocker)
    response = res_mock.return_value

    in_use_mock = https_mock if protocol == 'https' else http_mock
    other_mock = http_mock if protocol == 'https' else https_mock

    in_use_mock.return_value.getresponse.return_value = response
    response.getcode.return_value = 200
    response.read.return_value = b'content'

    fetch_result = fetch(f'{protocol}://{HOST}', {})

    in_use_mock.assert_called_once_with(HOST)
    other_mock.assert_not_called()

    fetch_content = assert_ok(fetch_result)
    assert fetch_content == 'content'


@pytest.mark.parametrize('tcase', ['getresponse', 'request'])
def test_http_fail_req_vs_res(mocker: MockerFixture, tcase: str):
    https_mock, _, _ = mock_http_connection(mocker)
    http_inst = https_mock.return_value
    getattr(http_inst, tcase).side_effect = Exception(f'fail {tcase}')
    fetch_result = fetch(f'https://{HOST}', {})
    failure_type = 'response' if tcase == 'getresponse' else 'request'
    err = assert_issue(fetch_result, f'https {failure_type} failure')
    ex = err.cause
    assert isinstance(ex, Exception)
    assert str(ex) == f'fail {tcase}'


def test_http_fetch_read_fail(mocker: MockerFixture):
    https_mock, _, res_mock = mock_http_connection(mocker)
    response = res_mock.return_value
    https_inst = https_mock.return_value
    https_inst.getresponse.return_value = response
    response.getcode.return_value = 200
    response.read.side_effect = Exception('fail read')
    fetch_result = fetch(f'https://{HOST}', {})
    assert_issue(fetch_result, 'https read failure')
    ex = cast(Issue, fetch_result.value).cause
    assert isinstance(ex, Exception)
    assert str(ex) == 'fail read'


def test_fetch_https_body(mocker: MockerFixture):
    https_mock, _, res_mock = mock_http_connection(mocker)
    response = res_mock.return_value
    https_inst = https_mock.return_value
    https_inst.getresponse.return_value = response
    response.getcode.return_value = 200
    response.read.return_value = b'content'
    fetch_result = fetch(f'https://{HOST}', {}, body='{"a":1}')
    https_mock.assert_called_once_with(HOST)
    https_inst.request.assert_called_once_with(
        'GET',
        '',
        '{"a":1}',
        {'user-agent': 'm', 'content-length': '7'},
    )
    assert_ok(fetch_result)


def test_fetch_https_server_err(mocker: MockerFixture):
    https_mock, _, res_mock = mock_http_connection(mocker)
    response = res_mock.return_value
    https_inst = https_mock.return_value
    https_inst.getresponse.return_value = response
    response.getcode.return_value = 500
    response.read.return_value = b'server error'
    fetch_result = fetch(f'https://{HOST}', {})
    https_mock.assert_called_once_with(HOST)
    assert_issue(fetch_result, 'https request failure (500)')
