from typing import Any, cast

from m.core.fp import OneOf
from m.core.issue import Issue


def assert_ok(either: OneOf[Issue, Any]) -> Any:
    assert either.is_bad is False, 'expecting ok'
    return either.value


def assert_issue(error: OneOf[Issue, Any], message: str | list[str]) -> Any:
    assert error.is_bad is True, 'expecting issue'
    err = cast(Issue, error.value)
    if isinstance(message, list):
        for err_msg in message:
            assert err_msg in err.message
    else:
        assert err.message == message
    return err
