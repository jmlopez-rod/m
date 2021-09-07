from ...core import Good, Issue, OneOf, issue
from .eslint import read_payload as read_eslint_payload
from .pycodestyle import read_payload as read_pycodestyle_payload
from .pylint import read_payload as read_pylint_payload
from .status import Linter, ToolConfig, linter


def get_linter(
    key: str,
    config: ToolConfig,
) -> OneOf[Issue, Linter]:
    """Find an available linter based on the key provided."""
    mapping = {
        'eslint': read_eslint_payload,
        'pycodestyle': read_pycodestyle_payload,
        'flake8': read_pycodestyle_payload,
        'pylint': read_pylint_payload,
    }
    if key not in mapping:
        return issue(f'{key} is not a supported linter')
    return Good(linter(key, config, mapping[key]))
