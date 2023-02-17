from functools import partial

import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, cli_params, run_cli
from tests.util import file_exists_mock, read_fixture_mock

FIXTURE_PATH = 'cli/commands/github/fixtures'
CMD = ('m', 'github', 'create_pr')


def _file_exists(name: str):
    """Having issues using partial with file_exists_mock."""
    return file_exists_mock(name, FIXTURE_PATH)


class TCase(CliTestCase):
    """Unit test case for github create_pr."""

    cmd: list[str]
    body_to_send: dict[str, str] | None = None
    new_line: bool = False


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--head': 'feature_branch',
                '--base': 'master',
                '--title': 'PR Title',
            }),
            'PR Title\n\nPR Body',
        ],
        body_to_send={
            'base': 'master',
            'body': 'PR Title\n\nPR Body',
            'head': 'feature_branch',
            'title': 'PR Title',
        },
    ),
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--head': 'feature_branch',
                '--base': 'master',
                '--title': 'PR Title',
            }),
            '@create_pr.txt',
        ],
        body_to_send={
            'base': 'master',
            'body': 'PR Title\n\nPR body in File\n',
            'head': 'feature_branch',
            'title': 'PR Title',
        },
    ),
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--head': 'feature_branch',
                '--base': 'master',
                '--title': 'PR Title',
            }),
            '@invalid-file.txt',
        ],
        errors=[
            'argument body: file "invalid-file.txt" does not exist',
        ],
        exit_code=2,
    ),
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--head': 'feature_branch',
                '--base': 'master',
                '--title': 'PR Title',
            }),
            '\\@jmlopez-rod - pr title',
        ],
        body_to_send={
            'base': 'master',
            'body': '@jmlopez-rod - pr title',
            'head': 'feature_branch',
            'title': 'PR Title',
        },
    ),
    TCase(
        cmd=[
            *CMD,
            *cli_params({
                '--owner': 'fake',
                '--repo': 'hotdog',
                '--head': 'feature_branch',
                '--base': 'master',
                '--title': 'PR Title',
            }),
        ],
        std_in='PR Title from stdin',
        body_to_send={
            'base': 'master',
            'body': 'PR Title from stdin',
            'head': 'feature_branch',
            'title': 'PR Title',
        },
    ),
])
def test_github_create_pr(tcase: TCase, mocker: MockerFixture) -> None:
    fetch_json = mocker.patch('m.core.http.fetch_json')
    fetch_json.return_value = Good('not_testing_output')

    mocker.patch('pathlib.Path.exists', _file_exists)
    mocker.patch(
        'pathlib.Path.open',
        partial(
            read_fixture_mock,
            mocker=mocker,
            path=FIXTURE_PATH,
        ),
    )

    if tcase.std_in:
        stdin_read = mocker.patch('sys.stdin.read')
        stdin_read.return_value = tcase.std_in

    _, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)

    if tcase.body_to_send:
        url, _, method, body = fetch_json.call_args[0]
        assert url == 'https://api.github.com/repos/fake/hotdog/pulls'
        assert method == 'POST'
        assert body == tcase.body_to_send
    assert_streams('', std_err, tcase)
