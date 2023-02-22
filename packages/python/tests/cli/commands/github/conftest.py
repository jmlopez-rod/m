import json
from functools import partial
from typing import Any

import yaml
from tests.fixture_utils import read_fixture

get_fixture = partial(
    read_fixture,
    path='cli/commands/github/fixtures',
)


def get_json_fixture(name: str) -> Any:
    return json.loads(get_fixture(name))


def get_yaml_fixture(name: str) -> Any:
    return yaml.safe_load(get_fixture(name))
