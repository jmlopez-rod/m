import sys
from typing import List, Dict, TextIO, Any

from ...core import OneOf, Good, Issue
from .status import Message, Result, ProjectStatus, lint


def read_payload(payload: List[Dict[str, Any]]) -> OneOf[Issue, List[Result]]:
    """Transform the eslint payload to a list of python objects that we can use
    to process the information."""
    return Good([
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
        for item in payload
    ])


def linter(
    payload: List[Dict[str, Any]],
    config: Dict[str, Any],
    stream: TextIO = sys.stdout
) -> OneOf[Issue, ProjectStatus]:
    """format the eslint output. """
    return lint(payload, read_payload, config, 'allowedEslintRules', stream)
