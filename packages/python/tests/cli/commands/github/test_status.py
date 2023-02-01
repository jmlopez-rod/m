import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import run_cli


class TCase(CliTestCase):
    """Unit test case for github status."""

    cmd: list[str]
    body_to_send: dict[str, str]


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            'm', 'github', 'status',
            '--owner', 'fake',
            '--repo', 'hotdog',
            '--sha', 'SHA',
            '--context', 'github-check',
            '--state', 'pending',
            '--description', 'running checks',
        ],
        body_to_send={
            'context': 'github-check',
            'state': 'pending',
            'description': 'running checks',
        }
    ),
    TCase(
        cmd=[
            'm', 'github', 'status',
            '--owner', 'fake',
            '--repo', 'hotdog',
            '--sha', 'SHA',
            '--context', 'github-check',
            '--state', 'pending',
            '--description', 'running checks',
            '--url', 'https://url-info'
        ],
        body_to_send={
            'context': 'github-check',
            'state': 'pending',
            'description': 'running checks',
            'target_url': 'https://url-info',
        }
    ),
])
def test_github_status(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.return_value = Good('not_testing_output')
    run_cli(tcase.cmd, tcase.exit_code, mocker)
    url, _, method, body = fetch_json.call_args[0]
    assert url == 'https://api.github.com/repos/fake/hotdog/statuses/SHA'
    assert method == 'POST'
    assert body == tcase.body_to_send
