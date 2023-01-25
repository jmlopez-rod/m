from subprocess import CalledProcessError

from m.core import subprocess
from pytest_mock import MockerFixture
from tests.conftest import assert_issue


def test_m_git_subprocess(mocker: MockerFixture) -> None:
    check_output = mocker.patch('subprocess.check_output')
    check_output.return_value = b'mocked output'
    test_res = subprocess.eval_cmd('echo "hello"')
    assert not test_res.is_bad
    assert test_res.value == 'mocked output'


def test_m_git_subprocess_error(mocker: MockerFixture) -> None:
    err = CalledProcessError(1, 'fake command', b'', b'mocked error')
    check_output = mocker.patch('subprocess.check_output')
    check_output.side_effect = err
    test_res = subprocess.eval_cmd('echo "hello"')
    assert_issue(test_res, 'command returned a non zero exit code')
