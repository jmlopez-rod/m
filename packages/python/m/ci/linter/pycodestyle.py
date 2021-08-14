import re
from typing import List, Dict

from ...core import OneOf, Issue, Good
from .status import Message, Result


def read_payload(payload: str) -> OneOf[Issue, List[Result]]:
    """Transform the pycodestyle payload to a list of Result objects."""
    regex = r'(.*):(\d+):(\d+): (\w+) (.*)'
    lines = payload.splitlines()
    data: Dict[str, List[Message]] = dict()
    for line in lines:
        match = re.match(regex, line)
        if match:
            file_path, line, col, rule_id, message = match.groups()
            item = Message(
                rule_id=rule_id,
                message=message,
                line=int(line),
                column=int(col),
                file_path=file_path,
            )
            if item.file_path not in data:
                data[item.file_path] = []
            data[item.file_path].append(item)
    return Good([
        Result(file_path=name, messages=items)
        for name, items in data.items()
    ])
