from typing import List

from ....core import Issue, OneOf, json, one_of
from ..core.types import FileReport, Violation


def read_payload(payload: str) -> OneOf[Issue, List[FileReport]]:
    """Transform an eslint payload to a list of `FileReport` instances.

    Args:
        payload: The raw payload from eslint.

    Returns:
        A `OneOf` containing an `Issue` or a list of `FileReport` instances.
    """
    return one_of(lambda: [
        [
            FileReport(
                file_path=error['filePath'],
                violations=[
                    Violation(
                        msg['ruleId'],
                        msg['message'],
                        msg['line'],
                        msg['column'],
                        error['filePath'],
                    )
                    for msg in error['messages']
                ],
            )
            for error in json_payload
        ]
        for json_payload in json.parse_json(payload)
    ])
