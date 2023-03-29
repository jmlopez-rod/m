from functools import partial
from typing import Any

from m.core import Issue, issue
from m.core.fp import Good, OneOf
from tests.cli.conftest import TCase as CliTestCase
from tests.fixture_utils import read_fixture

get_fixture = partial(
    read_fixture,
    path='cli/commands/review_release/fixtures',
)


def read_file_fake(filename: str, f_map: dict) -> OneOf[Issue, str]:
    """Fake read_file function for testing.

    Args:
        filename: The filename to read.
        f_map: A map of filenames to fixture names.

    Returns:
        The contents of the fixture.
    """
    fname = f_map.get(filename)
    if not fname:
        return issue('filename not mapped', context={'filename': filename})
    return Good(get_fixture(fname))


class TCase(CliTestCase):
    """Unit test case for end_release."""

    cmd: str = 'm review_release'
    exit_code: int = 1
    branch: str = 'master'
    user_input: list[str] = []
    graphql_response: str = 'no_prs.json'
    merge_result: list[Any] = []
    create_prs: list[Any] = []
    gh_latest: list[str] = ['0.0.1']
    git_commit_result: Any = Good('[mocked git commit]')
    m_file: str = 'm.json'
    pr_body_has: str | None = None
