from functools import partial
from typing import Any

from m.core import Issue, issue
from m.core.fp import Good, OneOf
from tests.cli.conftest import TCase as CliTestCase
from tests.fixture_utils import read_fixture

get_fixture = partial(
    read_fixture,
    path='cli/commands/start_release/fixtures',
)


def read_file_fake(filename: str, f_map: dict) -> OneOf[Issue, str]:
    fname = f_map.get(filename)
    if not fname:
        return issue('filename not mapped', context={'filename': filename})
    return Good(get_fixture(fname))


class TCaseErr(CliTestCase):
    """Unit test case for errors in release_setup."""

    exit_code: int = 1
    branch: str = 'master'
    user_input: list[str] = []
    status: tuple[str, str] = ('clean', 'clean msg')
    version: str = '0.0.1'
    # Its a test, and pydantic does not support the OneOf type...
    git_stash: Any = Good('it has been stashed')
    git_stash_pop: Any = Good('stash popped')
    changelog: str | None = None
    commits: list[str] | str = []
    git_checkout: Any = Good('git has checked out a branch')


class TCase(CliTestCase):
    """Unit test case for errors in release_setup."""

    delta_link: str
    changelog: str
    m_file: str
    diff_cl: list[str]
    diff_mf: list[str]
