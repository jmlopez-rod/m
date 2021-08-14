from typing import List

from ...core import OneOf, Issue, one_of, json
from .status import Message, Result


def read_payload(payload: str) -> OneOf[Issue, List[Result]]:
    """Transform the eslint payload to a list of python objects that we can use
    to process the information."""
    return one_of(lambda: [
        [
            Result(
                file_path=item['filePath'],
                messages=[
                    Message(
                        msg['ruleId'],
                        msg['message'],
                        msg['line'],
                        msg['column'],
                        item['filePath'],
                    )
                    for msg in item['messages']
                ]
            )
            for item in json_payload
        ]
        for json_payload in json.parse_json(payload)
    ])
