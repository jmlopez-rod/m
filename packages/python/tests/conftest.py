from typing import Any, TypeVar, cast

from m.core.fp import OneOf
from m.core.issue import Issue

G = TypeVar('G')  # pylint: disable=invalid-name


def assert_ok(either: OneOf[Issue, G]) -> G:
    assert either.is_bad is False, 'expecting ok'
    return cast(G, either.value)


def assert_issue(error: OneOf[Issue, Any], message: str | list[str]) -> Issue:
    assert error.is_bad is True, 'expecting issue'
    err = cast(Issue, error.value)
    if isinstance(message, list):
        for err_msg in message:
            assert err_msg in err.message
    else:
        assert err.message == message
    return err
