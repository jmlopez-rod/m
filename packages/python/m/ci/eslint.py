import os
import enum
from dataclasses import dataclass
from typing import Callable, List, Dict, Any

from ..core import OneOf, one_of, Good, Issue, json, io


class ExitCode(enum.Enum):
    """One of the possible exit codes."""
    OK = 0
    ERROR = 1
    NEEDS_READJUSTMENT = 2


@dataclass
class Message:
    """A message object containing information about the eslint rule that was
    triggered.

    https://eslint.org/docs/developer-guide/working-with-custom-formatters#the-result-object
    """  # noqa
    rule_id: str
    message: str
    line: int
    column: int
    # Not part of eslint. Adding here to make it easier to process data.
    file_path: str


@dataclass
class Result:
    """A result object for each file reported to have errors in eslint.

    https://eslint.org/docs/developer-guide/working-with-custom-formatters#the-result-object
    """  # noqa
    file_path: str
    messages: List[Message]


@dataclass
class RuleIdStatus:
    """Stats about a rule."""
    rule_id: str
    found: int
    allowed: int
    messages: List[Message]


@dataclass
class ProjectStatus:
    """Status about a project."""
    status: ExitCode
    rules: Dict[str, RuleIdStatus]


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


def to_rules_dict(results: List[Result]) -> Dict[str, List[Message]]:
    """Convert the eslint Result object to a dictionary that maps eslint rules
    to messages."""
    obj: Dict[str, List[Message]] = dict()
    for result in results:
        for msg in result.messages:
            if msg.rule_id not in obj:
                obj[msg.rule_id] = []
            obj[msg.rule_id].append(msg)
    return obj


def get_project_status(
    rules_dict: Dict[str, List[Message]],
    allowed_rules: Dict[str, int],
) -> ProjectStatus:
    """Compare the rules_dict with the allowed rules to provide an easy to
    display project status."""
    rules: Dict[str, RuleIdStatus] = {}
    failed = False
    needs_readjustment = False
    for rule_id, messages in rules_dict.items():
        total_messages = len(messages)
        allowed = allowed_rules.get(rule_id, 0)
        if total_messages > allowed:
            failed = True
        elif total_messages < allowed:
            needs_readjustment = True
        rules[rule_id] = RuleIdStatus(
            rule_id,
            total_messages,
            allowed,
            messages,
        )
    status = ExitCode.OK
    if failed:
        status = ExitCode.ERROR
    elif needs_readjustment:
        status = ExitCode.NEEDS_READJUSTMENT
    return ProjectStatus(status, rules)


def format_rule_status(rule: RuleIdStatus) -> str:
    """Formats a single rule and its violations."""
    buffer = [f'{rule.rule_id} (found {rule.found}, allowed {rule.allowed}):']
    max_lines = 5
    cwd = os.getcwd() + '/'
    for msg in rule.messages[:max_lines]:
        file_path = msg.file_path.replace(cwd, '')
        buffer.append(f'  {msg.line}:{msg.column}:{file_path} - {msg.message}')
    if len(rule.messages) > max_lines:
        buffer.append(f'  ... and {len(rule.messages) - max_lines} more')
    buffer.append('')
    return '\n'.join(buffer)


def _alignv(value: Any, alignment: str) -> Callable[[int], str]:
    return str(value).ljust if alignment == 'l' else str(value).rjust


def format_row(
    values: List[Any],
    widths: List[int],
    alignment: str,
) -> str:
    """Format a row to be displayed in a table"""
    items = [
        val
        for index, align in enumerate(alignment)
        for val in (_alignv(values[index], align)(widths[index]),)
    ]
    return '  '.join(items)


def print_project_status(project: ProjectStatus) -> OneOf[Issue, int]:
    """Status report"""
    keys = project.rules.keys()
    values = project.rules.values()
    blocks = [
        format_rule_status(rule)
        for rule in values if rule.found > rule.allowed
    ]

    c1_w = max([len(x) for x in keys])
    c1_w = max([c1_w, len('rules')])
    c2_w = max([len(str(s.found)) for s in values])
    c2_w = max([c2_w, len('found')])
    c3_w = max([len(str(s.allowed)) for s in values])
    c3_w = max([c3_w, len('allowed')])
    widths = [c1_w, c2_w, c3_w]

    blocks.append(format_row(['RULES', 'FOUND', 'ALLOWED'], widths, 'lll'))
    blocks.extend([
        format_row(
            [rule_id, rule_status.found, rule_status.allowed],
            widths,
            'lrr'
        )
        for rule_id, rule_status in project.rules.items()
    ])
    print('\n'.join(blocks))
    print()

    total_found = sum([s.found for s in values])
    total_allowed = sum([s.allowed for s in values])
    if project.status == ExitCode.ERROR:
        diff = total_found - total_allowed
        io.CiTool.error(f'{diff} extra errors were introduced')
    elif project.status == ExitCode.NEEDS_READJUSTMENT:
        diff = total_allowed - total_found
        io.CiTool.error(f'{diff} errors were removed - lower error allowance')
    else:
        print(f'project has {total_found} errors to clear')
    return Good(0)


def eslint(
    payload: List[Dict[str, Any]],
    config: Dict[str, Any],
) -> OneOf[Issue, ProjectStatus]:
    """format the eslint output. """
    return one_of(lambda: [
        project_status
        for data in read_payload(payload)
        for rules_dict in (to_rules_dict(data),)
        for allowed_rules in json.get(config, 'allowedEslintRules')
        for project_status in (get_project_status(rules_dict, allowed_rules),)
        for _ in print_project_status(project_status)
    ])
