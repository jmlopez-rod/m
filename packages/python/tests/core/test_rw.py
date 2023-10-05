from functools import partial
from pathlib import Path

from m.core import rw
from pytest_mock import MockerFixture
from tests import originals
from tests.conftest import assert_issue, assert_ok
from tests.util import read_fixture_mock

original_write_file = originals['write_file']

def test_rw_read(mocker: MockerFixture) -> None:
    mocker.patch(
        'pathlib.Path.open',
        partial(
            read_fixture_mock,
            mocker=mocker,
            path='_fixtures',
        ),
    )
    res_either = rw.read_file('test_reading.txt')
    file_contents = assert_ok(res_either)
    assert file_contents == 'hello world\n'

    res_either = rw.read_file('invalid')
    assert_issue(res_either, 'failed to read file')


def test_rw_write(mocker: MockerFixture) -> None:
    # restore write file to test it
    rw.write_file = original_write_file
    open_mock = mocker.mock_open()
    mocker.patch('pathlib.Path.open', open_mock, create=True)
    res = rw.write_file('some_file.txt', 'hello there')

    open_mock.assert_called_with(Path('some_file.txt'), 'w', encoding='UTF-8')
    open_mock.return_value.write.assert_called_once_with('hello there')
    assert res.value == 0


def test_rw_write_fail(mocker: MockerFixture) -> None:
    # restore write file to test it
    mocked_func = rw.write_file
    rw.write_file = original_write_file

    open_mock = mocker.mock_open()
    mocker.patch('pathlib.Path.open', open_mock, create=True)
    open_mock.return_value = Exception('oops')
    res = rw.write_file('some_file.txt', 'hello there')

    # mocking again to prevent writing files
    rw.write_file = mocked_func

    open_mock.assert_called_with(Path('some_file.txt'), 'w', encoding='UTF-8')
    assert_issue(res, 'failed to write file')
