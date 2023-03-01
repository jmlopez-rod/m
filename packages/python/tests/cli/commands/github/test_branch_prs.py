import os

import pytest
import yaml
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import cli_params, run_cli

from .conftest import get_json_fixture, get_yaml_fixture


class TCase(CliTestCase):
    """Unit test case for github pr."""

    cmd: list[str]
    response_files: list[str]
    expected_file: str
    cleandoc: bool = False
    new_line: bool = False
    total_lines: int = 1


CMD = ('m', 'github', 'branch_prs')


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'jmlopez-rod',
                '--repo': 'git_flow',
            }),
            'hotfix/0.5.1',
        ],
        response_files=['branch_pr.json'],
        expected_file='branch_pr_expected.json',
    ),
    TCase(
        cmd=[
            *CMD,
            '--pretty',
            *cli_params({
                '--owner': 'jmlopez-rod',
                '--repo': 'git_flow',
            }),
            'hotfix/0.5.1',
        ],
        response_files=['branch_pr.json'],
        expected_file='branch_pr_expected.json',
        total_lines=-1,
    ),
    TCase(
        cmd=[
            *CMD,
            '--yaml',
            *cli_params({
                '--owner': 'jmlopez-rod',
                '--repo': 'git_flow',
            }),
            'hotfix/0.5.1',
        ],
        response_files=['branch_pr.json'],
        expected_file='branch_pr_expected.yaml',
        total_lines=23,
    ),
])
def test_github_branch_prs(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'NO_COLOR': 'true', 'GITHUB_TOKEN': 'super_secret'},
        clear=True,
    )
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.side_effect = [
        Good(get_json_fixture(file_name))
        for file_name in tcase.response_files
    ]
    std_out, _ = run_cli(tcase.cmd, tcase.exit_code, mocker)
    expected_json = (
        get_json_fixture(tcase.expected_file)
        if tcase.expected_file.endswith('.json')
        else get_yaml_fixture(tcase.expected_file)
    )
    if tcase.total_lines != -1:
        assert len(std_out.splitlines()) == tcase.total_lines
    assert yaml.safe_load(std_out) == expected_json
