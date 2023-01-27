import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli

from .conftest import get_json_fixture


class TCase(CliTestCase):
    """Unit test case for github build_sha."""

    cmd: list[str]
    response_files: list[str]


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            'm', 'github', 'build_sha',
            '--owner', 'jmlopez-rod',
            '--repo', 'm',
            '--sha', '6bf3a8095891c551043877b922050d5b01d20284',
        ],
        response_files=['build_sha.json'],
        expected='fa6a600729ffbe1dfd7fece76ef4566e45fbfe40'
    ),
    TCase(
        cmd=[
            'm', 'github', 'build_sha',
            '--owner', 'jmlopez-rod',
            '--repo', 'unknown-repo',
            '--sha', 'unknown',
        ],
        response_files=['build_sha_error.json'],
        errors=[
            'github graphql errors',
            'some error message'
        ],
        exit_code=1,
    ),
])
def test_github_build_sha(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.side_effect = [
        Good(get_json_fixture(file_name))
        for file_name in tcase.response_files
    ]
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
