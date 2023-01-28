import unittest
from os import path as pth
from typing import Any, List, TypeVar, cast

from m.core.fp import OneOf
from m.core.issue import Issue
from pytest_mock import MockerFixture

T = TypeVar('T')

def read_fixture(name: str, path: str = 'ci/fixtures') -> str:
    """Read a json file from the given path.

    Args:
        name: The name of the fixture file.
        path: The directory of the fixture (defaults to ci/fixtures).

    Returns:
        The contents of the file.
    """
    with open(f'packages/python/tests/{path}/{name}', encoding='UTF-8') as fp:
        return fp.read()


def read_fixture_mock(
    name: str,
    path: str,
    mocker: MockerFixture,
    **kwargs,
):
    """Mock the return value of `open`.

    Args:
        name: The name of the fixture file.
        path: The directory of the fixture (defaults to ci/fixtures).
        mocker: The mocker instance.
        _kwargs: Any other argument that may be passed to the open function.

    Returns:
        A value to use as a mock for the `open` function.
    """
    mock = mocker.mock_open(read_data=read_fixture(name, path))
    return mock.return_value


def file_exists_mock(name: str, path: str) -> bool:
    """Check if a file exists in the given path.

    Args:
        name: The name of the fixture file.
        path: The directory of the fixture.

    Returns:
        True if it exists.
    """
    return pth.exists(f'packages/python/tests/{path}/{name}')


def compare_values(test_case, tests: List[Any]) -> None:
    """Compare multiple values without calling assertEqual on each line.

        self.assertEqual(a, 1)
        self.assertEqual(b, 2, 'message')

    same as

        compare_values(self, [[a, 1], [b, 2, 'message']])

    Args:
        test_case: The instance of a Test.
        tests: An array of value that should be the same.
    """
    for test in tests:
        x, y, *msg = test
        test_case.assertEqual(x, y, msg and msg[0] or None)


class FpTestCase(unittest.TestCase):
    """Utility class with fp friendly methods."""

    def assert_issue(
        self,
        error: OneOf[Issue, Any],
        message: str,
    ) -> Any:
        self.assertTrue(error.is_bad, 'expecting issue')
        err = cast(Issue, error.value)
        self.assertEqual(err.message, message)
        return err

    def assert_ok(self, either: OneOf[Issue, T]) -> T:
        self.assertFalse(either.is_bad, 'expecting ok')
        return cast(T, either.value)
