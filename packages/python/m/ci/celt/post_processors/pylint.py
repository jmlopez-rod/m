from typing import Any, Dict, List, cast

from ....core import Good, Issue, OneOf, json
from ..core.types import FileReport, Violation


def read_payload(payload: str) -> OneOf[Issue, List[FileReport]]:
    """Transform a pylint payload to a list of `FileReport` instances.

    Args:
        payload: The raw payload from pylint.

    Returns:
        A `OneOf` containing an `Issue` or a list of `FileReport` instances.
    """
    res = json.parse_json(payload)
    if res.is_bad:
        return res
    violations = cast(List[Any], res.value)
    report: Dict[str, List[Violation]] = {}
    for v_item in violations:
        violation = Violation(
            rule_id=v_item['symbol'],
            message=v_item['message'],
            line=int(v_item['line']),
            column=int(v_item['column']),
            file_path=v_item['path'],
        )
        if violation.file_path not in report:
            report[violation.file_path] = []
        report[violation.file_path].append(violation)
    return Good([
        FileReport(file_path=name, violations=violations)
        for name, violations in report.items()
    ])
