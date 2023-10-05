from typing import Any

from pydantic import BaseModel
from tests.cli.conftest import TCase as BaseTCase


class WriteArgs(BaseModel):
    path: str
    fname: str


class TCase(BaseTCase):
    """Test case for `m github actions`."""

    name: str
    cmd: str = 'm github actions'
    py_file: str
    checks: bool = False
    write_calls: list[WriteArgs] = []
    mock_actions: Any | None = None
    read_calls: list[Any] = []
