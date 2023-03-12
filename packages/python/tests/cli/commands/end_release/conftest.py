from functools import partial
from typing import Any

from m.core import Issue, issue
from m.core.fp import Good, OneOf
from tests.cli.conftest import TCase as CliTestCase
from tests.fixture_utils import read_fixture

get_fixture = partial(
    read_fixture,
    path='cli/commands/end_release/fixtures',
)


def read_file_fake(filename: str, f_map: dict) -> OneOf[Issue, str]:
    fname = f_map.get(filename)
    if not fname:
        return issue('filename not mapped', context={'filename': filename})
    return Good(get_fixture(fname))


class TCase(CliTestCase):
    """Unit test case for end_release."""

    exit_code: int = 1
    branch: str = 'master'
    user_input: list[str] = []
    graphql_response: str = ''
    merge_result: list[Any] = []
    gh_latest: list[str] = ['0.0.1']
