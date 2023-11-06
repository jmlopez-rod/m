from __future__ import annotations

from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    TypeGuard,
    TypeVar,
    Union,
    cast,
)

import typing_extensions

# Note: disabling WPS110 in .flake8 for this file.
#   Reason for this, the variable name "value".
A = TypeVar('A')  # pylint: disable=invalid-name
B = TypeVar('B')  # pylint: disable=invalid-name
G = TypeVar('G')  # pylint: disable=invalid-name
K = TypeVar('K')  # pylint: disable=invalid-name
LazyArg = Union[A, Callable[[], A]]


def lazy_arg(z_arg: LazyArg[A]) -> A:
    """Return the output of calling `z_arg` if it is function.

    Otherwise param is returned.

    Args:
        z_arg: A function or a value

    Returns:
        The value.
    """
    return z_arg() if callable(z_arg) else z_arg


class StopBadIteration(Exception):  # noqa: N818 - This is for internal use
    """Store a `Bad` instance."""

    def __init__(self, bad: Any):
        """Initialize the Exception.

        Args:
            bad: The `Bad` value stored in a `OneOf`.
        """
        super().__init__()
        self.bad = bad


class Bad(Generic[B, G]):
    """The bad side of the disjoint union."""

    value: B
    is_bad = True

    def __init__(self, value: B):
        """Initialize a `Bad` instance.

        Args:
            value: The "bad" value to store in the instance.
        """
        self.value = value

    def __iter__(self) -> Iterator[G]:
        """Iterate over values of an instance.

        The intention is to raise a `StopBadIteration` exception to
        be able to break out of for loop comprehensions.

        Raises:
            StopBadIteration: If the instance has a "Bad" value.
        """
        raise StopBadIteration(self)

    def iter(self) -> Iterator[G]:
        """Shortcut to transform to a list.

        Can be used as `list(x.iter())`. It will either contain a value or be
        an empty list.

        Yields:
            The value if the instance is a "Good" value.
        """
        empty = ()
        yield from empty

    def get_or_else(self, default: LazyArg[G]) -> G:
        """Return the value if its Good or the given argument if its a Bad.

        Args:
            default: The default value in case the instance is "Bad".

        Returns:
            Either the value or the default specified by "default".
        """
        return lazy_arg(default)

    def map(self, _fct: Callable[[G], K]) -> 'Bad[B, K]':
        """Apply the function to its value if this is a `Good` instance.

        Args:
            _fct: The function to apply to the "Good" value.

        Returns:
            Itself if its a `Bad` otherwise another instance of `Good`.
        """
        return cast(Bad[B, K], self)

    def flat_map_bad(self, fct: Callable[[B], OneOf[B, G]]) -> OneOf[B, G]:
        """Apply the input function if this is a `Bad` value.

        Args:
            fct: The function to apply to the "Bad" value.

        Returns:
            Itself if its a `Good` otherwise another instance of `Bad`.
        """
        return fct(self.value)


class Good(Generic[B, G]):
    """The good side of the disjoint union."""

    value: G
    is_bad = False

    def __init__(self, value: G):
        """Initialize a `Good` instance.

        Args:
            value: The "good" value to store in the instance.
        """
        self.value = value

    def __iter__(self) -> Iterator[G]:
        """Iterate over the value of the instance.

        Yields:
            The value of the instance.
        """
        yield self.value

    def iter(self) -> Iterator[G]:
        """Shortcut to transform to a list.

        Can be used as `list(x.iter())`. It will either contain a value or be
        an empty list.

        Yields:
            The value if the instance is a "Good" value.
        """
        if not self.is_bad:
            yield self.value

    def get_or_else(self, _default: LazyArg[G]) -> G:
        """Return the value.

        Args:
            _default: The default value in case the instance is "Bad".

        Returns:
            Either the value or the default specified by "default".
        """
        return self.value

    def map(self, fct: Callable[[G], K]) -> 'Good[B, K]':
        """Apply the function to its value if this is a `Good` instance.

        Args:
            fct: The function to apply to the "Good" value.

        Returns:
            Itself if its a `Bad` otherwise another instance of `Good`.
        """
        return Good(fct(self.value))

    def flat_map_bad(self, _fct: Callable[[B], OneOf[B, G]]) -> OneOf[B, G]:
        """Apply the input function if this is a `Bad` value.

        Args:
            _fct: The function to apply to the "Bad" value.

        Returns:
            Itself if its a `Good` otherwise another instance of `Bad`.
        """
        return self


OneOf = Bad[B, G] | Good[B, G]


@typing_extensions.deprecated(
    'The `is_bad` type guard is deprecated; use `isinstance(inst, Bad)` instead.',
)
def is_bad(inst: OneOf[B, G]) -> TypeGuard[Bad[B, G]]:
    """Assert that a OneOf instance is a `Bad`.

    Args:
        inst: The `OneOf` instance.

    Returns:
        True if the instance is a `Bad`.
    """
    # `m` does not reference this function anymore, excluding from coverage
    return isinstance(inst, Bad)  # pragma: no cover


@typing_extensions.deprecated(
    'The `is_good` type guard is deprecated; use `isinstance(inst, Good)` instead.',
)
def is_good(inst: OneOf[B, G]) -> TypeGuard[Good[B, G]]:
    """Assert that a OneOf instance is a `Good`.

    Args:
        inst: The `OneOf` instance.

    Returns:
        True if the instance is a `Good`.
    """
    # `m` does not reference this function anymore, excluding from coverage
    return isinstance(inst, Good)  # pragma: no cover
