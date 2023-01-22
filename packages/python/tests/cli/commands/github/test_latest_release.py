import os

import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli

from .conftest import get_json_fixture


class TCase(CliTestCase):
    """Unit test case for github latests_release."""

    cmd: str | list[str] = 'm github latest_release --owner fake --repo hotdog'
    response_file: str


@pytest.mark.parametrize('tcase', [
    TCase(
        response_file='latest_release_no_releases.json',
        expected='0.0.0',
    ),
    TCase(
        response_file='latest_release_good.json',
        expected='0.11.2',
    ),
    TCase(
        exit_code=1,
        response_file='latest_release_bad.json',
        errors=[
            "Could not resolve to a Repository with the name 'fake/hotdog'"
        ],
    ),
    TCase(
        exit_code=1,
        response_file='latest_release_unknown.json',
        errors=[
            "github response missing data field",
            # making sure we display the contents of the response
            "intentionally changing the response to see how m behaves",
        ],
    ),
])
def test_github_latest_release(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    if tcase.response_file != 'skip':
        fetch_json.side_effect = [Good(get_json_fixture(tcase.response_file))]
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)


def test_github_latest_release_access(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)
    cmd=[
        'm', 'github',
        '--token', '',
        'latest_release',
        '--owner', 'fake',
        '--repo', 'hotdog',
    ]
    _, std_err = run_cli(cmd, 2, mocker)
    assert 'argument -t/--token: empty value not allowed' in std_err
