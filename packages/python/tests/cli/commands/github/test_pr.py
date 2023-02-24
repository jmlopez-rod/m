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


CMD = ('m', 'github', 'pr')


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'microsoft',
                '--repo': 'typescript',
            }),
            '44710',
        ],
        response_files=['pr.json'],
        expected_file='pr_expected.json',
    ),
    TCase(
        cmd=[
            *CMD,
            '--pretty',
            *cli_params({
                '--owner': 'microsoft',
                '--repo': 'typescript',
            }),
            '44710',
        ],
        response_files=['pr.json'],
        expected_file='pr_expected.json',
        total_lines=36,
    ),
    TCase(
        cmd=[
            *CMD,
            '--yaml',
            '--pretty',
            *cli_params({
                '--owner': 'microsoft',
                '--repo': 'typescript',
            }),
            '44710',
        ],
        response_files=['pr.json'],
        expected_file='pr_expected.yaml',
        total_lines=30,
    ),
    TCase(
        cmd=[
            *CMD,
            '--yaml',
            *cli_params({
                '--owner': 'microsoft',
                '--repo': 'typescript',
            }),
            '44710',
        ],
        response_files=['pr.json'],
        expected_file='pr_expected.yaml',
        total_lines=30,
    ),
])
def test_github_pr(tcase: TCase, mocker: MockerFixture) -> None:
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
    expected_json = (
        get_json_fixture(tcase.expected_file)
        if tcase.expected_file.endswith('.json')
        else get_yaml_fixture(tcase.expected_file)
    )
    std_out, _ = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert len(std_out.splitlines()) == tcase.total_lines
    assert yaml.safe_load(std_out) == expected_json


def _throw_error():
    raise RuntimeError('oops')


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            *CMD,
            '--pretty',
            '--yaml',
            *cli_params({
                '--owner': 'microsoft',
                '--repo': 'typescript',
            }),
            '44710',
        ],
        response_files=['pr.json'],
        expected_file='pr_expected.yaml',
        total_lines=30,
    ),
])
def test_github_pr_highlight_fail(tcase: TCase, mocker: MockerFixture) -> None:
    # Making sure highlighting issues will not ruin the day
    # Main point is to enable colors. Here we can see that by calling yaml
    # we can still parse the output because the pygment function failed to
    # do its thing. This is not normal operation but the color is just to
    # display pretty output to the dev and not meant to do CI things.
    mocker.patch.dict(
        os.environ,
        {'NO_COLOR': 'false', 'GITHUB_TOKEN': 'super_secret'},
        clear=True,
    )
    mocker.patch('m.color.pygment.highlight', _throw_error)
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.side_effect = [
        Good(get_json_fixture(file_name))
        for file_name in tcase.response_files
    ]
    expected_json = (
        get_json_fixture(tcase.expected_file)
        if tcase.expected_file.endswith('.json')
        else get_yaml_fixture(tcase.expected_file)
    )

    std_out, _ = run_cli(tcase.cmd, tcase.exit_code, mocker)
    # This next line would fail if highlight was able to do its job
    # remember that we sabotaged it with a bad function so it failed, thus
    # we get the text as is.
    assert len(std_out.splitlines()) == tcase.total_lines
    assert yaml.safe_load(std_out) == expected_json
