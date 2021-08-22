from typing import List, Dict, Any, cast

from ...core import OneOf, Issue, Good, json
from .status import Message, Result


def read_payload(payload: str) -> OneOf[Issue, List[Result]]:
    """Transform the pylint payload to a list of Result objects."""
    res = json.parse_json(payload)
    if res.is_bad:
        return res
    items = cast(List[Any], res.value)
    data: Dict[str, List[Message]] = {}
    for item in items:
        msg = Message(
            rule_id=item['symbol'],
            message=item['message'],
            line=int(item['line']),
            column=int(item['column']),
            file_path=item['path'],
        )
        if msg.file_path not in data:
            data[msg.file_path] = []
        data[msg.file_path].append(msg)
    return Good([
        Result(file_path=name, messages=items)
        for name, items in data.items()
    ])
