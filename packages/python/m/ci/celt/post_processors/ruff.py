from m.core import Good, Res, hone, json, one_of
from m.pydantic import parse_model
from pydantic import BaseModel

from ..core.types import FileReport, Violation


class Location(BaseModel):
    """A location in a file."""

    row: int
    column: int


class RuffViolation(BaseModel):
    """A violation from ruff."""

    code: str
    filename: str
    location: Location
    message: str


Report = dict[str, list[Violation]]


def _index_violations(violations: list[RuffViolation]) -> Res[Report]:
    report: Report = {}
    for v_item in violations:
        violation = Violation(
            rule_id=v_item.code,
            message=v_item.message,
            line=v_item.location.row,
            column=v_item.location.column,
            file_path=v_item.filename,
        )
        if violation.file_path not in report:
            report[violation.file_path] = []
        report[violation.file_path].append(violation)
    return Good(report)


def read_payload(payload: str) -> Res[list[FileReport]]:
    """Transform a pylint payload to a list of `FileReport` instances.

    Args:
        payload: The raw payload from pylint.

    Returns:
        A `OneOf` containing an `Issue` or a list of `FileReport` instances.
    """
    context = {'suggestion': 'run ruff check --format json'}
    return one_of(lambda: [
        [
            FileReport(file_path=name, violations=violations)
            for name, violations in report.items()
        ]
        for json_payload in json.parse_json(payload)
        for violations in parse_model(list[RuffViolation], json_payload)
        for report in _index_violations(violations)
    ]).flat_map_bad(hone('invalid_ruff_output_payload', context))
