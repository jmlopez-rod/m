import os

import pytest
from m.core import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli
from tests.util import read_fixture

FIXTURE_PATH = '_blueprints/fixtures'
M_DIR = 'packages/python/tests/_blueprints/m_dir'


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=f'm blueprints --update-workflow --update-makefile {M_DIR}',
        expected='',
    ),
])
def test_m_blueprints(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)
    mocker.patch('time.time').return_value = 123456789
    mocker.patch('pathlib.Path.mkdir')
    file_write_mock = mocker.patch('m.core.rw.write_file')
    file_write_mock.return_value = Good(0)

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)

    calls = file_write_mock.call_args_list
    _assert_call(calls[0], ('../Makefile', 'Makefile'))
    _assert_call(calls[1], ('../.github/workflows/m.yaml', 'gh_m.yaml'))
    _assert_call(
        calls[2],
        (
            '.m/blueprints/local/m-image1.build.sh',
            'local/m-image1.build.sh',
        ),
    )
    _assert_call(
        calls[3],
        (
            '.m/blueprints/local/m-image2.build.sh',
            'local/m-image2.build.sh',
        ),
    )
    _assert_call(
        calls[4],
        (
            '.m/blueprints/ci/_find-cache.sh',
            'ci/_find-cache.sh',
        ),
    )
    _assert_call(
        calls[5],
        (
            '.m/blueprints/ci/_push-image.sh',
            'ci/_push-image.sh',
        ),
    )
    _assert_call(
        calls[6],
        (
            '.m/blueprints/ci/m-image1.build.sh',
            'ci/m-image1.build.sh',
        ),
    )
    _assert_call(
        calls[7],
        (
            '.m/blueprints/ci/m-image2.build.sh',
            'ci/m-image2.build.sh',
        ),
    )
    _assert_call(
        calls[8],
        (
            '.m/blueprints/ci/_image-names.json',
            'ci/_image-names.json',
        ),
    )
    _assert_call(
        calls[9],
        (
            '.m/blueprints/ci/_image-tags.json',
            'ci/_image-tags.json',
        ),
    )


def _assert_call(call, expected):
    assert call.args[0] == f'{M_DIR}/{expected[0]}'
    assert call.args[1] == read_fixture(expected[1], FIXTURE_PATH)
