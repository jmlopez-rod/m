from datetime import datetime
from difflib import unified_diff
from functools import partial
from typing import List, Optional
from unittest.mock import MagicMock

from m.core import Issue, issue
from m.core.fp import Good, OneOf
from pydantic import BaseModel
from pytest import ExceptionInfo
from tests.fixture_utils import read_fixture


get_fixture = partial(
    read_fixture,
    path='cli/commands/ci/release_setup/fixtures'
)


def read_file_fake(filename: str, f_map: dict) -> OneOf[Issue, str]:
    fname = f_map.get(filename)
    if not fname:
        return issue('filename not mapped', context={ 'filename': filename })
    return Good(get_fixture(fname))


def _get_diffs(text_a: str, text_b: str) -> List[str]:
    list_a = text_a.splitlines(keepends=True)
    list_b = text_b.splitlines(keepends=True)
    diff = unified_diff(list_a, list_b, fromfile='before', tofile='after')
    return [line for line in diff]


class TCaseErr(BaseModel):
    """Unit test case for errors in release_setup."""

    exit_code: int = 1
    std_out: str
    std_err: str
    args: List[str]
    changelog: Optional[str]


class TCase(BaseModel):
    """Unit test case for errors in release_setup."""

    delta_link: str
    args: List[str] = ['m', '1.2.3']
    changelog: str
    m_file: str
    diff_cl: List[str]
    diff_mf: List[str]


def assert_err(
    prog: ExceptionInfo[SystemExit],
    std_err: str,
    tcase: TCaseErr,
) -> None:
    """Assert program exit code and stderr contents.

    Args:
        prog: The program exception info.
        std_err: An instance of StringIO with the contents of std_err.
        tcase: The test case object containing the expected results.
    """
    assert prog.value.code == tcase.exit_code
    assert tcase.std_err in std_err


def assert_result(
    prog: ExceptionInfo[SystemExit],
    std_out: str,
    write_file_mock: MagicMock,
    tcase: TCase,
) -> None:
    """Assert program exit code and stderr contents.

    Args:
        std_err: An instance of StringIO with the contents of std_err.
        tcase: The test case object containing the expected results.
    """
    assert prog.value.code == 0
    assert tcase.delta_link in std_out
    # date = datetime.now().strftime('%B %d, %Y')
    m_file_call = write_file_mock.call_args_list[0]
    # changelog_call = write_file_mock.call_args_list[1]
    actual_diff_mf = _get_diffs(r_fixture(tcase.m_file), m_file_call.args[1])
    assert actual_diff_mf == tcase.diff_mf

