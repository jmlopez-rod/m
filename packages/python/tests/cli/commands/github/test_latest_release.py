import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import assert_streams, run_cli

from .conftest import TCase, get_json_fixture


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
    tcase.cmd = 'm github latest_release --owner fake --repo hotdog'
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.side_effect = [Good(get_json_fixture(tcase.response_file))]
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
