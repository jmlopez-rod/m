from typing import Callable, Any, Dict, TextIO

from ...core import OneOf, Issue, issue, Good
from .status import ProjectStatus, Linter, linter
from .eslint import read_payload as read_eslint_payload


def get_linter(key: str) -> OneOf[Issue, Linter]:
    """Find an available linter based on the key provided."""
    mapping = dict(
        eslint=linter('eslint', read_eslint_payload),
    )
    if key not in mapping:
        return issue(f'{key} is not a supported linter')
    return Good(mapping[key])
