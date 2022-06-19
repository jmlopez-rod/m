import enum
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from ....core import Issue, OneOf


class ExitCode(enum.Enum):
    """One of the possible exit codes."""

    ok = 0
    error = 1
    needs_readjustment = 2


@dataclass
class Violation:
    """An error/warning/message provided by a compiler or linter."""

    rule_id: str
    message: str
    line: int
    column: int
    file_path: str


@dataclass
class FileReport:
    """Collection of violations triggered in a single file."""

    file_path: str
    violations: List[Violation]


@dataclass
class RuleInfo:
    """Stats on a rule."""

    rule_id: str
    violations: List[Violation]
    found: int
    allowed: int = 0
    ignored: bool = False


@dataclass
class ProjectStatus:
    """Overview of a project."""

    status: ExitCode
    payload: str
    rules: Dict[str, RuleInfo]
    files: Dict[str, List[Violation]]
    total_found: int = field(init=False)
    total_allowed: int = field(init=False)
    error_msg: str = field(init=False)

    def __post_init__(self):
        """Compute the rest of non initialized variables."""
        rules = self.rules.values()
        total_found = sum((s.found for s in rules if not s.ignored))
        total_allowed = sum((s.allowed for s in rules if not s.ignored))
        error_msg = ''
        if self.status == ExitCode.error:
            diff = sum((
                d
                for s in rules
                for d in (s.found - s.allowed,)
                if d > 0 and not s.ignored
            ))
            error_msg = f'{diff} extra errors were introduced'
        elif self.status == ExitCode.needs_readjustment:
            diff = total_allowed - total_found
            error_msg = f'{diff} errors were removed - lower error allowance'

        self.total_found = total_found  # noqa: WPS601
        self.total_allowed = total_allowed  # noqa: WPS601
        self.error_msg = error_msg  # noqa: WPS601


@dataclass
class Configuration:
    """Options to control the output of the post processor."""

    max_lines: int = 5
    full_message: bool = False
    ignore_error_allowance: bool = False
    file_regex: Optional[str] = None
    file_prefix: Optional[str] = None


Transform = Callable[[str], OneOf[Issue, List[FileReport]]]
