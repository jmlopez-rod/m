import json
from functools import partial
from typing import Any

from tests.fixture_utils import read_fixture

get_fixture = partial(
    read_fixture,
    path='cli/commands/github/fixtures'
)


def get_json_fixture(name: str) -> Any:
    return json.loads(get_fixture(name))
