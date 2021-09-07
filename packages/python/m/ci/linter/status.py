import enum
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TextIO

from ...core import Good, Issue, OneOf, io, one_of


class ExitCode(enum.Enum):
    """One of the possible exit codes."""
    OK = 0
    ERROR = 1
    NEEDS_READJUSTMENT = 2


@dataclass
class Message:
    """A message object containing information about a rule that was
    triggered."""
    rule_id: str
    message: str
    line: int
    column: int
    file_path: str


@dataclass
class Result:
    """A result object for each file reported to have errors."""
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
    files: Dict[str, List[Message]]


@dataclass
class ToolConfig:
    """Configuration to use for the linter."""
    max_lines: int = 5
    full_message: bool = False
    file_regex: Optional[str] = None


def to_rules_dict(results: List[Result]) -> Dict[str, List[Message]]:
    """Convert the list of Result objects to a dictionary that maps rules to
    Messages."""
    obj: Dict[str, List[Message]] = {}
    for result in results:
        for msg in result.messages:
            if msg.rule_id not in obj:
                obj[msg.rule_id] = []
            obj[msg.rule_id].append(msg)
    return obj


def get_project_status(
    results: List[Result],
    rules_dict: Dict[str, List[Message]],
    allowed_rules: Dict[str, int],
) -> ProjectStatus:
    """Compare the rules_dict with the allowed rules to provide an easy to
    display project status."""
    files: Dict[str, List[Message]] = {
        x.file_path: x.messages
        for x in results
    }
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
    return ProjectStatus(status, rules, files)


def format_rule_status(
    rule: RuleIdStatus,
    config: ToolConfig,
) -> str:
    """Formats a single rule and its violations."""
    buffer = [f'{rule.rule_id} (found {rule.found}, allowed {rule.allowed}):']
    cwd = os.getcwd() + '/'
    for msg in rule.messages[:config.max_lines]:
        file_path = msg.file_path.replace(cwd, '')
        _msg, *rest = msg.message.splitlines()
        buffer.append(f'  {file_path}:{msg.line}:{msg.column} - {_msg}')
        if rest and config.full_message:
            buffer.extend([f'    {x}' for x in rest])
    if len(rule.messages) > config.max_lines:
        buffer.append(
            f'  ... and {len(rule.messages) - config.max_lines} more',
        )
    buffer.append('')
    return '\n'.join(buffer)


def _alignv(value: Any, alignment: str) -> Callable[[int], str]:
    return str(value).ljust if alignment == 'l' else str(value).rjust


def format_row(
    values: List[Any],
    widths: List[int],
    alignment: str,
) -> str:
    """Format a row to be displayed in a table."""
    items = [
        val
        for index, align in enumerate(alignment)
        for val in (_alignv(values[index], align)(widths[index]),)
    ]
    return '  '.join(items)


def print_project_status(
    project: ProjectStatus,
    config: ToolConfig,
    stream: TextIO = sys.stdout,
) -> OneOf[Issue, int]:
    """Status report."""
    keys = project.rules.keys()
    values = sorted(project.rules.values(), key=lambda r: r.found)
    total_found = sum([s.found for s in values])
    total_allowed = sum([s.allowed for s in values])

    if project.status == ExitCode.OK:
        if total_found > 0:
            print(f'project has {total_found} errors to clear', file=stream)
        else:
            print('no errors found', file=stream)
        return Good(0)

    blocks = [
        format_rule_status(rule, config)
        for rule in values if rule.found > rule.allowed
    ]

    blocks.append('FILES:')
    by_file = sorted(project.files.items(), key=lambda t: len(t[1]))
    blocks.extend([
        f'  {file_name}: found {len(messages)}'
        for file_name, messages in by_file
    ])
    blocks.append('')

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
            'lrr',
        )
        for rule_id, rule_status in sorted(
            project.rules.items(),
            key=lambda x: x[1].found,
        )
    ])
    print('\n'.join(blocks), file=stream)
    print('', file=stream)

    if project.status == ExitCode.ERROR:
        diff = sum([
            d
            for s in values
            for d in (s.found - s.allowed,) if d > 0
        ])
        io.CiTool.error(
            f'{diff} extra errors were introduced',
            stream=stream,
        )
    elif project.status == ExitCode.NEEDS_READJUSTMENT:
        diff = total_allowed - total_found
        io.CiTool.error(
            f'{diff} errors were removed - lower error allowance',
            stream=stream,
        )
    return Good(0)


def filter_results(
    results: List[Result],
    config: ToolConfig
) -> List[Result]:
    """Filter the list of results based on the file path.
    """
    regex = config.file_regex
    return [
        x
        for x in results
        if not regex or re.match(regex, x.file_path)
    ]


def lint(
    payload: str,
    transform: Callable[[str], OneOf[Issue, List[Result]]],
    config: Dict[str, Any],
    config_key: str,
    tool_config: ToolConfig,
    stream: TextIO = sys.stdout,
) -> OneOf[Issue, ProjectStatus]:
    """format the linter tool output."""
    return one_of(lambda: [
        project_status
        for results in transform(payload)
        for filtered in (filter_results(results, tool_config),)
        for rules_dict in (to_rules_dict(filtered),)
        for allowed_rules in (config.get(config_key, {}),)
        for project_status in (
            get_project_status(filtered, rules_dict, allowed_rules),
        )
        for _ in print_project_status(project_status, tool_config, stream)
    ])


Linter = Callable[[Any, Dict[str, Any], TextIO], OneOf[Issue, ProjectStatus]]


def linter(
    name: str,
    tool_config: ToolConfig,
    transform: Callable[[str], OneOf[Issue, List[Result]]],
) -> Linter:
    """Generate a linter based on the tool name and its tranform."""
    def _linter(
        payload: str,
        config: Dict[str, Any],
        stream: TextIO = sys.stdout,
    ) -> OneOf[Issue, ProjectStatus]:
        key = f'allowed{name.capitalize()}Rules'
        return lint(payload, transform, config, key, tool_config, stream)

    return _linter
