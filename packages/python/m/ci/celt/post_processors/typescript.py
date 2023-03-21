import re

from m.ci.celt.core.types import FileReport, Violation
from m.core import Good, Issue, OneOf


def read_payload(payload: str) -> OneOf[Issue, list[FileReport]]:
    """Transform a typescript payload to a list of `FileReport` instances.

    Args:
        payload: The raw payload from typescript when `--pretty false` option.

    Returns:
        A `OneOf` containing an `Issue` or a list of `FileReport` instances.
    """
    regex = r'(.*)\((\d+),(\d+)\): error (\w+): (.*)'
    report: dict[str, list[Violation]] = {}
    for line in payload.splitlines():
        if line.startswith(' '):
            continue
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
