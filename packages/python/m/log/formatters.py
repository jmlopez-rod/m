import json
import logging
import textwrap

from .ci_tools.ci_tools import get_ci_tool
from .ci_tools.types import Message


class JsonFormatter(logging.Formatter):
    def format(self, record):
        record_dict = record.__dict__
        context = record_dict.get('context')
        ci_info = record_dict.get('ci_info', Message(msg=record.msg))
        replacements = {
            **record_dict,
            **ci_info.dict(),
            'asctime': self.formatTime(record, self.datefmt),
            'context': context,
        }
        replacements.pop('ci_info', '')
        sanitized = {
            key: non_empty
            for key, non_empty in replacements.items()
            if non_empty
        }
        return json.dumps(sanitized)


class CiFormatter(logging.Formatter):
    """A formatter that takes into account a CI environment.

    We can still use
    """

    def __init__(
        self,
        datefmt: str = '%I:%M:%S %p - %b %d, %Y',
    ):
        super().__init__(datefmt=datefmt)
        self.opened_blocks: list[str] = []
        self.ci_tool = get_ci_tool()

    def format(self, record):
        msg = self.ci_tool.formatter(self, record)
        if self.ci_tool.ci:
            return msg

        record_dict = record.__dict__
        open_b = record_dict.get('open_block')
        close_b = record_dict.get('close_block')

        if open_b:
            name, _ = open_b
            self.opened_blocks.append(name)
        if close_b:
            while self.opened_blocks and self.opened_blocks[-1] != close_b:
                self.opened_blocks.pop()
            if self.opened_blocks:
                self.opened_blocks.pop()

        if not self.opened_blocks:
            return msg
        return textwrap.indent(msg, '  ' * len(self.opened_blocks))
