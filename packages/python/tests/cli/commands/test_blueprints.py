import os

import pytest
from m.core import Good
from pydantic import BaseModel
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as BaseTCase
from tests.cli.conftest import assert_streams, run_cli
from tests.util import read_fixture


class WriteArgs(BaseModel):
    path: str
    fname: str


class TCase(BaseTCase):
    """Test case for `m blueprints`."""

    cmd: str = 'm blueprints'
    options: str
    fixture_path: str
    m_dir: str
    write_calls: list[WriteArgs]


@pytest.mark.parametrize('tcase', [
    TCase(
        options='--update-workflow --update-makefile',
        expected='',
        fixture_path='blueprints/multi-arch/fixtures',
        m_dir='packages/python/tests/blueprints/multi-arch/m',
        write_calls=[
            WriteArgs(
                path='../Makefile',
                fname='Makefile',
            ),
            WriteArgs(
                path='../.github/workflows/m.yaml',
                fname='gh-m.yaml',
            ),
            WriteArgs(
                path='.m/blueprints/local/m-image1.build.sh',
                fname='local/m-image1.build.sh',
            ),
            WriteArgs(
                path='.m/blueprints/local/m-image2.build.sh',
                fname='local/m-image2.build.sh',
            ),
            WriteArgs(
                path='.m/blueprints/ci/_find-cache.sh',
                fname='ci/_find-cache.sh',
            ),
            WriteArgs(
                path='.m/blueprints/ci/_push-image.sh',
                fname='ci/_push-image.sh',
            ),
            WriteArgs(
                path='.m/blueprints/ci/m-image1.build.sh',
                fname='ci/m-image1.build.sh',
            ),
            WriteArgs(
                path='.m/blueprints/ci/m-image2.build.sh',
                fname='ci/m-image2.build.sh',
            ),
            WriteArgs(
                path='.m/blueprints/ci/_image-names.json',
                fname='ci/_image-names.json',
            ),
            WriteArgs(
                path='.m/blueprints/ci/_image-tags.json',
                fname='ci/_image-tags.json',
            ),
        ],
    ),
])
def test_m_blueprints(tcase: TCase, mocker: MockerFixture) -> None:
    """Verify blueprints write all the necessary files."""
    mocker.patch.dict(os.environ, {}, clear=True)
    mocker.patch('time.time').return_value = 123456789
    mocker.patch('pathlib.Path.mkdir')
    file_write_mock = mocker.patch('m.core.rw.write_file')
    file_write_mock.return_value = Good(0)

    cmd = f'{tcase.cmd} {tcase.options} {tcase.m_dir}'
    std_out, std_err = run_cli(cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)

    calls = file_write_mock.call_args_list
    assert len(calls) == len(tcase.write_calls)
    for index, ex_call in enumerate(tcase.write_calls):
        call = calls[index]
        assert call.args[0] == f'{tcase.m_dir}/{ex_call.path}'
        assert call.args[1] == read_fixture(ex_call.fname, tcase.fixture_path)
