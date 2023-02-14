from typing import Callable, Generic, Iterator, TypeGuard, TypeVar, Union, cast

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

    def __init__(self, bad):
        """Initialize the Exception.

        Args:
            bad: The `Bad` value stored in a `OneOf`.
        """
        super().__init__()
        self.bad = bad


class OneOf(Generic[B, G]):
    """An instance of `OneOf` is an instance of either `Bad` or `Good`."""

    is_bad: bool
    value: B | G

    def __init__(self, bad: bool, value: B | G):
        """Initialize a `OneOf`.

        Args:
            bad:
                Set to `True` if the instance holds a `Bad` value.
            value:
                The value of the instance.
        """
        self.is_bad = bad
        self.value = value

    def __iter__(self) -> Iterator[G]:
        """Iterate over instances that contain a "good" value.

        Yields:
            The value if the instance is a "Good" value.

        Raises:
            StopBadIteration: If the instance has a "Bad" value.
        """
        if self.is_bad:
            raise StopBadIteration(self)
        yield cast(G, self.value)

    def iter(self):
        """Shortcut to transform to a list.

        Can be used as `list(x.iter())`. It will either contain a value or be
        an empty list.

        Yields:
            The value if the instance is a "Good" value.
        """
        if not self.is_bad:
            yield self.value

    def map(self, fct: Callable[[G], K]) -> 'OneOf[B, K]':
        """Apply the function to its value if this is a `Good` instance.

        Args:
            fct: The function to apply to the "Good" value.

        Returns:
            Itself if its a `Bad` otherwise another instance of `Good`.
        """
        return (
            cast(OneOf[B, K], self)
            if self.is_bad
            else Good(fct(cast(G, self.value)))
        )

    def flat_map_bad(self, fct: Callable[[B], 'OneOf']) -> 'OneOf':
        """Apply the input function if this is a `Bad` value.

        Args:
            fct: The function to apply to the "Bad" value.

        Returns:
            Itself if its a `Good` otherwise another instance of `Bad`.
        """
        return fct(cast(B, self.value)) if self.is_bad else self

    def get_or_else(self, default: LazyArg[G]) -> G:
        """Return the value if its Good or the given argument if its a Bad.

        Args:
            default: The default value in case the instance is "Bad".

        Returns:
            Either the value or the default specified by "default".
        """
        return lazy_arg(default) if self.is_bad else cast(G, self.value)


class Bad(OneOf[B, G]):
    """The bad side of the disjoint union."""

    is_bad: bool = False
    value: B

    def __init__(self, one_of_value: B):
        """Initialize a `Bad` instance.

        Args:
            one_of_value: The "bad" value.
        """
        super().__init__(bad=True, value=one_of_value)


class Good(OneOf[B, G]):
    """The good side of the disjoint union."""

    is_bad: bool = False
    value: G

    def __init__(self, one_of_value):
        """Initialize a `Bad` instance.

        Args:
            one_of_value: The "bad" value.
        """
        super().__init__(bad=False, value=one_of_value)


def is_bad(inst: OneOf[B, G]) -> TypeGuard[Bad[B, G]]:
    """Assert that a OneOf instance is a `Bad`.

    Args:
        inst: The `OneOf` instance.

    Returns:
        True if the instance is a `Bad`.
    """
    return inst.is_bad


def is_good(inst: OneOf[B, G]) -> TypeGuard[Good[B, G]]:
    """Assert that a OneOf instance is a `Good`.

    Args:
        inst: The `OneOf` instance.

    Returns:
        True if the instance is a `Good`.
    """
    return not inst.is_bad
