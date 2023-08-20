from typing import TypeVar

from .fp import OneOf
from .issue import Issue

G = TypeVar('G')  # pylint: disable=invalid-name

# A type alias for a `OneOf` that has an `Issue` on the bad side.
# This is useful for functions that return a `OneOf` that can fail
# with an `Issue`. Shortening for `Result`, `Response` or `Resolution`.
Res = OneOf[Issue, G]
