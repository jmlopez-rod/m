import json

import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import cli_params, run_cli

from .conftest import get_json_fixture


class TCase(CliTestCase):
    """Unit test case for github latests_release."""

    cmd: list[str]
    response_files: list[str]
    expected_file: str
    cleandoc: bool = False
    new_line: bool = False


CMD = ('m', 'github', 'ci')


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--sha': '4538b2a2556efcbdfc1e7df80c4f71ade45f3958',
                '--pr': '1',
            }),
            '--include-release',
        ],
        response_files=['ci_simple.json'],
        expected_file='ci_simple_expected.json',
    ),
    TCase(
        cmd=[
            *CMD,
            '--merge-commit',
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--sha': '4538b2a2556efcbdfc1e7df80c4f71ade45f3958',
            }),
        ],
        response_files=['ci_no_merge_1.json', 'ci_no_merge_2.json'],
        expected_file='ci_no_merge_expected.json',
    ),
])
def test_github_latest_release(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.side_effect = [
        Good(get_json_fixture(file_name))
        for file_name in tcase.response_files
    ]
    expected_json = get_json_fixture(tcase.expected_file)
    std_out, _ = run_cli(tcase.cmd, tcase.exit_code, mocker)

    assert json.loads(std_out) == expected_json
