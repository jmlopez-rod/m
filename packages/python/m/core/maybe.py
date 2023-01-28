from typing import Callable, TypeVar

T = TypeVar('T')


def maybe(callback: Callable[[], T]) -> T | None:
    """Evaluate the callback to return a value.

    Unlike Typescript, Python does not have optional chaining::

        https://en.wikipedia.org/wiki/Safe_navigation_operator#Python

    To simulate this we can use this function as follows::

        ans = maybe(lambda: path.to.prop)  # type: ignore[union-attr]

    It is ok to disable the `union-attr` mypy check as long as mypy is checking
    for `no-any-return`.

    Args:
        callback: A function return a value.

    Returns:
        The value returned by the function or `None`.
    """
    try:
        return callback()
    except AttributeError:
        return None


def non_null(inst: T | None) -> T:
    """Assert that `inst` is not `None`.

    Implementation taken from::

        https://github.com/python/typing/issues/645#issuecomment-501057220

    Args:
        inst: A possibly null instance.

    Returns:
        The same argument with the `None` type removed.
    """
    # The assert statement can go away with the -O flag.
    assert inst is not None  # noqa: S101
    return inst
