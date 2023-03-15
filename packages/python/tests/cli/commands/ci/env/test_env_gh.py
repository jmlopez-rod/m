import json
import os
from functools import partial
from typing import Any

import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import run_cli
from tests.util import read_fixture, read_fixture_mock

FIXTURE_PATH = 'cli/commands/ci/env/fixtures'


def _get_fixture(name: str):
    return read_fixture(name, FIXTURE_PATH)


def get_json_fixture(name: str) -> Any:
    return json.loads(_get_fixture(name))


GH_ENV = {
    'DEBUG_HTTP_INCLUDE_BODY': '1',
    'GITHUB_ACTIONS': 'true',
    'GITHUB_REPOSITORY': '',
    'GITHUB_RUN_ID': '404',
    'GITHUB_RUN_NUMBER': '99',
    'GITHUB_TOKEN': 'super-duper-secret',
    'GITHUB_REF': 'refs/heads/master',
    'GITHUB_SHA': 'abc123',
    'GITHUB_ACTOR': 'jmlopez-rod',
}


class TCase(CliTestCase):
    env_vars: dict[str, str]
    m_list_file: str
    m_list_contents: str
    response_files: list[str]


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m ci env m_dir_gh_m_flow',
        env_vars=GH_ENV,
        m_list_file='m_dir_gh_m_flow/.m/env.list',
        m_list_contents='m_dir_gh_m_flow/m_expected.list',
        response_files=[
            'm_dir_gh_m_flow/ci_simple.json',
            'm_dir_gh_m_flow/ci_simple.json',
        ],
    ),
])
def test_m_ci_env_gh(tcase: TCase, mocker: MockerFixture) -> None:
    # clear env vars to avoid ci tool specific messages
    mocker.patch.dict(os.environ, tcase.env_vars, clear=True)
    mocker.patch('m.ci.config.get_m_filename').return_value = Good(
        'm_dir_gh_m_flow/m.json',
    )
    mocker.patch('pathlib.Path.exists').return_value = True
    mocker.patch(
        'pathlib.Path.open',
        partial(
            read_fixture_mock,
            mocker=mocker,
            path=FIXTURE_PATH,
        ),
    )
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.side_effect = [
        Good(get_json_fixture(file_name))
        for file_name in tcase.response_files
    ]
    write_file_mock = mocker.patch('m.core.rw.write_file')
    write_file_mock.return_value = Good(None)

    run_cli(tcase.cmd, tcase.exit_code, mocker)
    write_file_mock.assert_called_once()
    file_name, file_contents = write_file_mock.call_args[0]
    assert file_name == tcase.m_list_file
    assert file_contents == _get_fixture(tcase.m_list_contents).strip()
