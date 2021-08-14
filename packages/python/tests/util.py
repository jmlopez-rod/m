import unittest
from typing import List, Any, cast
from m.core.issue import Issue
from m.core.fp import OneOf


def read_fixture(name: str, path: str = 'ci/fixtures') -> str:
    """Read a json file from the given path. Defaults to `ci/fixtures` since
    this is the place that deals with with the most payloads."""
    with open(f'packages/python/tests/{path}/{name}') as fp:
        return fp.read()


def compare_values(test_case, items: List[Any]) -> None:
    """Compare multiple values without callng assertEqual
    on each line.

        self.assertEqual(a, 1)
        self.assertEqual(b, 2, 'message')

    same as

        compare_values(self, [
            [a, 1],
            [b, 2, 'message'],
        ])

    """
    for item in items:
        x, y, *msg = item
        test_case.assertEqual(x, y, msg and msg[0] or None)


class FpTestCase(unittest.TestCase):
    """Utility class with fp friendly methods"""

    def assert_issue(
        self,
        error: OneOf[Issue, Any],
        message: str,
    ) -> Any:
        self.assertTrue(error.is_bad, 'expecting issue')
        err = cast(Issue, error.value)
        self.assertEqual(err.message, message)
        return err

    def assert_ok(self, either: OneOf[Issue, Any]) -> None:
        self.assertFalse(either.is_bad, 'expecting ok')
