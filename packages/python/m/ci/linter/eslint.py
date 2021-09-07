from typing import List

from ...core import Issue, OneOf, json, one_of
from .status import Message, Result


def read_payload(payload: str) -> OneOf[Issue, List[Result]]:
    """Transform an eslint payload to a list of `Result` objects.

    Args:
        payload: The raw payload from eslint

    Returns:
        A `OneOf` containing an `Issue` or a list of `Result` objects.
    """
    return one_of(lambda: [
        [
            Result(
                file_path=error['filePath'],
                messages=[
                    Message(
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
