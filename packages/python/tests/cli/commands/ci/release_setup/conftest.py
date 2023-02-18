from difflib import unified_diff
from functools import partial
from unittest.mock import MagicMock

from m.core import Issue, issue
from m.core.fp import Good, OneOf
from tests.cli.conftest import TCase as CliTestCase
from tests.fixture_utils import read_fixture

get_fixture = partial(
    read_fixture,
    path='cli/commands/ci/release_setup/fixtures',
)


def read_file_fake(filename: str, f_map: dict) -> OneOf[Issue, str]:
    fname = f_map.get(filename)
    if not fname:
        return issue('filename not mapped', context={'filename': filename})
    return Good(get_fixture(fname))


def _get_diffs(text_a: str, text_b: str) -> list[str]:
    list_a = text_a.splitlines(keepends=True)
    list_b = text_b.splitlines(keepends=True)
    diff = unified_diff(list_a, list_b, fromfile='before', tofile='after')
    return [line for line in diff]


class TCaseErr(CliTestCase):
    """Unit test case for errors in release_setup."""

    exit_code: int = 1
    changelog: str | None


class TCase(CliTestCase):
    """Unit test case for errors in release_setup."""

    delta_link: str
    changelog: str
    m_file: str
    diff_cl: list[str]
    diff_mf: list[str]


def assert_result(
    std_out: str,
    write_file_mock: MagicMock,
    tcase: TCase,
) -> None:
    """Assert program exit code and stderr contents.

    Args:
        std_out: The contents of stdout.
        write_file_mock: A mock instance of write_file.
        tcase: The test case object containing the expected results.
    """
    assert tcase.delta_link in std_out
    m_file_call = write_file_mock.call_args_list[0]
    actual_diff_mf = _get_diffs(get_fixture(tcase.m_file), m_file_call.args[1])
    assert actual_diff_mf == tcase.diff_mf

    changelog_call = write_file_mock.call_args_list[1]
    actual_diff_cl = _get_diffs(
        get_fixture(tcase.changelog),
        changelog_call.args[1],
    )
    assert actual_diff_cl == tcase.diff_cl
