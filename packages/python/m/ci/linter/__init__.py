from ...core import OneOf, Issue, issue, Good
from .status import Linter, linter
from .eslint import read_payload as read_eslint_payload
from .pycodestyle import read_payload as read_pycodestyle_payload
from .pylint import read_payload as read_pylint_payload


def get_linter(key: str, max_lines: int) -> OneOf[Issue, Linter]:
    """Find an available linter based on the key provided."""
    mapping = dict(
        eslint=read_eslint_payload,
        pycodestyle=read_pycodestyle_payload,
        pylint=read_pylint_payload,
    )
    if key not in mapping:
        return issue(f'{key} is not a supported linter')
    return Good(linter(key, max_lines, mapping[key]))
