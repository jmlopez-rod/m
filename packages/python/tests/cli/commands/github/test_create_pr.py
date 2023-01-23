import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import run_cli


class TCase(CliTestCase):
    """Unit test case for github create_pr."""

    cmd: list[str]
    body_to_send: dict[str, str]


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            'm', 'github', 'create_pr',
            '--owner', 'fake',
            '--repo', 'hotdog',
            '--head', 'feature_branch',
            '--base', 'master',
            '--title', 'PR Title',
            'PR Title\n\nPR Body',
        ],
        body_to_send={
            'base': 'master',
            'body': 'PR Title\n\nPR Body',
            'head': 'feature_branch',
            'title': 'PR Title',
        }
    ),
])
def test_github_create_pr(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.return_value = Good('not_testing_output')
    run_cli(tcase.cmd, tcase.exit_code, mocker)
    print(fetch_json.call_args)
    url, _, method, body = fetch_json.call_args[0]
    assert url == 'https://api.github.com/repos/fake/hotdog/pulls'
    assert method == 'POST'
    assert body == tcase.body_to_send
