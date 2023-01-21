import json
from functools import partial
from typing import Any

from tests.cli.conftest import TCase as CliTestCase
from tests.fixture_utils import read_fixture

get_fixture = partial(
    read_fixture,
    path='cli/commands/github/fixtures'
)


def get_json_fixture(name: str) -> Any:
    return json.loads(get_fixture(name))


class TCase(CliTestCase):
    """Unit test case for github latests_release."""

    cmd: str = 'm github latest_release --owner fake --repo hotdog'
    response_file: str
