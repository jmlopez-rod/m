import os
import sys
import enum
from dataclasses import dataclass
from typing import Callable, List, Dict, Any, TextIO

from ...core import OneOf, Good, Issue, io, one_of


class ExitCode(enum.Enum):
    """One of the possible exit codes."""
    OK = 0
    ERROR = 1
    NEEDS_READJUSTMENT = 2


@dataclass
class Message:
    """A message object containing information about a rule that was
    triggered. """
    rule_id: str
    message: str
    line: int
    column: int
    file_path: str


@dataclass
class Result:
    """A result object for each file reported to have errors. """
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


def to_rules_dict(results: List[Result]) -> Dict[str, List[Message]]:
    """Convert the list of Result objects to a dictionary that maps rules
    to Messages."""
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
    for rule_id, allowed in allowed_rules.items():
        if rule_id not in rules:
            rules[rule_id] = RuleIdStatus(
                rule_id,
                0,
                allowed,
                [],
            )
            if allowed > 0:
                needs_readjustment = True
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
        _msg = msg.message.splitlines()[0]
        buffer.append(f'  {file_path}:{msg.line}:{msg.column} - {_msg}')
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


def print_project_status(
    project: ProjectStatus,
    stream: TextIO = sys.stdout
) -> OneOf[Issue, int]:
    """Status report"""
    keys = project.rules.keys()
    values = project.rules.values()
    total_found = sum([s.found for s in values])
    total_allowed = sum([s.allowed for s in values])

    if project.status == ExitCode.OK:
        if total_found > 0:
            print(f'project has {total_found} errors to clear', file=stream)
        else:
            print('no errors found', file=stream)
        return Good(0)

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
    print('\n'.join(blocks), file=stream)
    print('', file=stream)

    if project.status == ExitCode.ERROR:
        diff = sum([
            d
            for s in values
            for d in (s.found - s.allowed, ) if d > 0
        ])
        io.CiTool.error(
            f'{diff} extra errors were introduced',
            stream=stream)
    elif project.status == ExitCode.NEEDS_READJUSTMENT:
        diff = total_allowed - total_found
        io.CiTool.error(
            f'{diff} errors were removed - lower error allowance',
            stream=stream)
    return Good(0)


def lint(
    payload: str,
    transform: Callable[[str], OneOf[Issue, List[Result]]],
    config: Dict[str, Any],
    config_key: str,
    stream: TextIO = sys.stdout
) -> OneOf[Issue, ProjectStatus]:
    """format the linter tool output. """
    return one_of(lambda: [
        project_status
        for data in transform(payload)
        for rules_dict in (to_rules_dict(data),)
        for allowed_rules in (config.get(config_key, {}),)
        for project_status in (get_project_status(rules_dict, allowed_rules),)
        for _ in print_project_status(project_status, stream)
    ])


Linter = Callable[[Any, Dict[str, Any], TextIO], OneOf[Issue, ProjectStatus]]


def linter(
    name: str,
    transform: Callable[[str], OneOf[Issue, List[Result]]],
) -> Linter:
    """Generate a linter based on the tool name and its tranform."""
    def _linter(
        payload: str,
        config: Dict[str, Any],
        stream: TextIO = sys.stdout
    ) -> OneOf[Issue, ProjectStatus]:
        key = f'allowed{name.capitalize()}Rules'
        return lint(payload, transform, config, key, stream)

    return _linter
