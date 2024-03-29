import unittest
from typing import Any, TypeVar

from m.core import OneOf, Res, one_of
from m.core.fp import Bad, Good
from m.core.maybe import non_null
from m.core.one_of import to_one_of
from tests.conftest import assert_issue

from ..util import compare_values

GenericT = TypeVar('GenericT')


def success_func() -> None:
    print('does nothing')  # noqa: WPS421


def failure_func() -> None:
    raise Exception('fails')


def identity(x: GenericT) -> GenericT:
    return x


class OneOfTest(unittest.TestCase):
    def test_instances(self) -> None:
        left: OneOf[bool, Any] = Bad(False)
        right: OneOf[Any, int] = Good(1)
        compare_values(self, [
            [left.is_bad, True, '"left" should be Bad(False)'],
            [right.is_bad, False, '"right" should be Good(1)'],
        ])

    def test_iteration(self) -> None:
        self.assertListEqual(list(Bad('err').iter()), [])
        self.assertListEqual(list(Good(100).iter()), [100])
        # Need this to trigger an unknown error
        bad = one_of(lambda x: x)  # type: ignore
        left: OneOf[Any, Any] = one_of(lambda: list(Bad('error')))
        right = one_of(lambda: list(Good(99)))
        self.assertIsInstance(bad, Bad)
        self.assertIsInstance(left, Bad)
        self.assertIsInstance(right, Good)
        self.assertEqual(left.value, 'error')
        self.assertEqual(right.value, 99)


def test_empty_one_of() -> None:
    bad: Res[int] = one_of(lambda: [])
    assert_issue(bad, 'one_of empty response - iteration missing a OneOf')


def test_fp_map() -> None:
    bad = Bad('to the bone').map(lambda _: 'not reachable')
    assert bad.is_bad
    assert bad.value == 'to the bone'
    good: OneOf[Any, str] = Good('x').map(lambda msg: f'{msg}^2')
    assert not good.is_bad
    assert isinstance(good, Good)
    assert good.value == 'x^2'


def test_to_one_of() -> None:
    good = to_one_of(success_func, 'will not fail')
    assert not good.is_bad
    assert good.value == 0
    bad = to_one_of(failure_func, 'failure message', {'data': 'helpful'})
    assert_issue(bad, 'failure message')


def _possibly_none() -> str | None:
    return 'some_value'


def test_non_null() -> None:
    possible_string = _possibly_none()
    # non_null is `!` from typescript. At times we need to help python
    # know that we have a non null value.
    string_for_real = non_null(possible_string)
    assert string_for_real == 'some_value'
