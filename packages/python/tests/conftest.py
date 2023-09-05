from typing import Any, TypeVar

from m.core.fp import Bad, Good, OneOf
from m.core.issue import Issue

G = TypeVar('G')  # pylint: disable=invalid-name


def assert_ok(either: OneOf[Issue, G]) -> G:
    """Assert that the `OneOf` is not an `Issue`.

    Args:
        either: `OneOf` to assert.

    Returns:
        The value contained in the `OneOf`.
    """
    assert isinstance(either, Good), 'expecting ok'
    return either.value


def assert_issue(error: OneOf[Issue, Any], message: str | list[str]) -> Issue:
    assert isinstance(error, Bad), 'expecting issue'
    err = error.value
    if isinstance(message, list):
        for err_msg in message:
            assert err_msg in err.message
    else:
        assert err.message == message
    return err
