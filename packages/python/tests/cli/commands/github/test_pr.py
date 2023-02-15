import json

import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import run_cli

from .conftest import get_json_fixture


class TCase(CliTestCase):
    """Unit test case for github pr."""

    cmd: list[str]
    response_files: list[str]
    expected_file: str
    cleandoc: bool = False
    new_line: bool = False
    total_lines: int = 1


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            'm', 'github', 'pr',
            '--owner', 'microsoft',
            '--repo', 'typescript',
            '44710',
        ],
        response_files=['pr.json'],
        expected_file='pr_expected.json',
    ),
    TCase(
        cmd=[
            'm', 'github', 'pr',
            '--pretty',
            '--owner', 'microsoft',
            '--repo', 'typescript',
            '44710',
        ],
        response_files=['pr.json'],
        expected_file='pr_expected.json',
        total_lines=36
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

    assert len(std_out.splitlines()) == tcase.total_lines
    assert json.loads(std_out) == expected_json
