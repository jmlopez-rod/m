from typing import Callable, Generic, Iterator, TypeVar, Union, cast

A = TypeVar('A')  # pylint: disable=invalid-name
B = TypeVar('B')  # pylint: disable=invalid-name
G = TypeVar('G')  # pylint: disable=invalid-name
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

    def __init__(self, bad: bool, one_of_value: Union[B, G]):
        """Initialize a `OneOf`.

        Args:
            bad:
                Set to `True` if the instance holds a `Bad` value.
            one_of_value:
                The value of the instance.
        """
        self.is_bad = bad
        self.value = one_of_value  # noqa: WPS110

    def __iter__(self) -> Iterator[G]:
        if self.is_bad:
            raise StopBadIteration(self)
        yield cast(G, self.value)

    def iter(self):
        """Shortcut to transform to a list: list(x.iter()).

        It will either contain a value or be an empty list.
        """
        if not self.is_bad:
            yield self.value

    def map(self, fct):
        """Apply the function to its value if this is a `Good` instance.

        Args:
            fct: The function to apply to the "Good" value.

        Returns:
            Itself if its a `Bad` otherwise another instance of `Good`.
        """
        return self if self.is_bad else Good(fct(self.value))

    def flat_map_bad(self, fct: Callable[[B], 'OneOf']) -> 'OneOf':
        """Apply the input function if this is a `Bad` value.

        Args:
            fct: The function to apply to the "Bad" value.

        Returns:
            Itself if its a `Good` otherwise another instance of `Bad`.
        """
        return fct(cast(B, self.value)) if self.is_bad else self

    def get_or_else(self, or_: LazyArg[G]) -> G:
        """Returns the value if its Good or the given argument if its a Bad."""
        return lazy_arg(or_) if self.is_bad else cast(G, self.value)


class Bad(OneOf[B, G]):
    """The bad side of the disjoint union."""

    def __init__(self, one_of_value):
        """Initialize a `Bad` instance.

        Args:
            one_of_value: The "bad" value.
        """
        super().__init__(bad=True, one_of_value=one_of_value)


class Good(OneOf[B, G]):
    """The good side of the disjoint union."""

    def __init__(self, one_of_value):
        """Initialize a `Good` instance.

        Args:
            one_of_value: The "good" value.
        """
        super().__init__(bad=False, one_of_value=one_of_value)
