import re
from typing import Dict, List

from ....core import Good, Issue, OneOf
from ..core.types import FileReport, Violation


def read_payload(payload: str) -> OneOf[Issue, List[FileReport]]:
    """Transform an pycodestyle payload to a list of `FileReport` instances.

    This function can be used with flake8 and other tools that emit similar
    output.

    Args:
        payload: The raw payload from pycodestyle.

    Returns:
        A `OneOf` containing an `Issue` or a list of `FileReport` instances.
    """
    regex = r'(.*):(\d+):(\d+): (\w+) (.*)'
    report: Dict[str, List[Violation]] = {}
    for line in payload.splitlines():
        match = re.match(regex, line)
        if match:
            group = match.groups()
            violation = Violation(
                file_path=group[0],
                line=int(group[1]),
                column=int(group[2]),
                rule_id=group[3],
                message=group[4],
            )
            if violation.file_path not in report:
                report[violation.file_path] = []
            report[violation.file_path].append(violation)
    return Good([
        FileReport(file_path=name, violations=violations)
        for name, violations in report.items()
    ])
