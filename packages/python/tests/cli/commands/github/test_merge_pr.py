import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import cli_params, run_cli


class TCase(CliTestCase):
    """Unit test case for github merge_pr."""

    cmd: list[str]
    body_to_send: dict[str, str]


CMD = ('m', 'github', 'merge_pr')


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
            }),
            '99',
        ],
        body_to_send={},
    ),
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--commit-title': 'some custom commit title',
            }),
            '99',
        ],
        body_to_send={
            'commit_title': 'some custom commit title',
        },
    ),
])
def test_github_merge_pr(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.return_value = Good('not_testing_output')
    run_cli(tcase.cmd, tcase.exit_code, mocker)
    url, _, method, body = fetch_json.call_args[0]
    assert url == 'https://api.github.com/repos/fake/hotdog/pulls/99/merge'
    assert method == 'PUT'
    assert body == tcase.body_to_send
