from typing import Any

import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import run_cli


class TCase(CliTestCase):
    """Unit test case for github release."""

    cmd: list[str]
    body_to_send: dict[str, Any]


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            'm', 'github', 'release',
            '--owner', 'fake',
            '--repo', 'hotdog',
            '--version', '1.0.0',
        ],
        body_to_send={
            'body': '**See '
                    '[CHANGELOG](https://github.com/fake/hotdog/blob/master/CHANGELOG.md#1.0.0).**',  # noqa E501
            'draft': False,
            'name': '1.0.0',
            'prerelease': False,
            'tag_name': '1.0.0',
        }
    ),
    TCase(
        cmd=[
            'm', 'github', 'release',
            '--owner', 'fake',
            '--repo', 'hotdog',
            '--version', '1.0.0',
            '--branch', 'production',
        ],
        body_to_send={
            'body': '**See '
                    '[CHANGELOG](https://github.com/fake/hotdog/blob/master/CHANGELOG.md#1.0.0).**',  # noqa E501
            'draft': False,
            'name': '1.0.0',
            'prerelease': False,
            'tag_name': '1.0.0',
            'target_commitish': 'production',
        }
    ),
])
def test_github_release(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.return_value = Good('not_testing_output')
    run_cli(tcase.cmd, tcase.exit_code, mocker)
    print(fetch_json.call_args)
    url, _, method, body = fetch_json.call_args[0]
    assert url == 'https://api.github.com/repos/fake/hotdog/releases'
    assert method == 'POST'
    assert body == tcase.body_to_send
