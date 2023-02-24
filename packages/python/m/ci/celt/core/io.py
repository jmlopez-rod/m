from functools import cmp_to_key
from typing import Any, Callable, List, Tuple

from m.color import color

from .types import Configuration, ExitCode, ProjectStatus, RuleInfo


def _compare_rules(rule_a: RuleInfo, rule_b: RuleInfo) -> int:
    diff = rule_a.found - rule_b.found or rule_a.allowed - rule_b.allowed
    if not diff:
        return 1 if rule_a.rule_id < rule_b.rule_id else -1
    return diff


def _compare_rule_items(
    rule_a: Tuple[str, RuleInfo],
    rule_b: Tuple[str, RuleInfo],
) -> int:
    return _compare_rules(rule_a[1], rule_b[1])


def _align(token: Any, alignment: str) -> Callable[[int], str]:
    return str(token).ljust if alignment == 'l' else str(token).rjust


def rule_info_str(
    rule: RuleInfo,
    config: Configuration,
) -> str:
    """Format a single rule and its violations.

    Args:
        rule: The rule to display.
        config: The post processor configuration.

    Returns:
        A string representation of the rule info.
    """
    allowed = 'IGNORED' if rule.ignored else f'allowed {rule.allowed}'
    rule_id = color(f'{{red}}{rule.rule_id}{{end}}')
    total_found = color(f'{{red}}{rule.found}{{end}}')
    buffer = [f'{rule_id} (found {total_found}, {allowed}):']
    violations = (
        rule.violations
        if config.max_lines == -1
        else rule.violations[:config.max_lines]
    )
    for violation in violations:
        file_path = violation.file_path
        msg, *rest = violation.message.splitlines()
        line = violation.line
        column = violation.column
        file_loc = color(f'{{gray}}{file_path}:{line}:{column}{{end}}')
        buffer.append(f'  {file_loc} - {msg}')
        if rest and config.full_message:
            buffer.extend([f'    {x}' for x in rest])
    if -1 < config.max_lines < len(rule.violations):
        remaining = len(rule.violations) - config.max_lines
        buffer.append(f'  ... and {remaining} more')
    buffer.append('')
    return '\n'.join(buffer)


def format_row(tokens: List[Any], widths: List[int], alignment: str) -> str:
    """Format a row to be displayed in a table.

    Args:
        tokens:
            A list of values to be displayed.
        widths:
            A list of integers of same size as tokens dictating the how many
            spaces to take for a token.
        alignment:
            Either 'l' or 'r' so that the tokens may be aligned on the left
            or right.

    Returns:
        A single string for a row of a table.
    """
    return '  '.join([
        token
        for index, align in enumerate(alignment)
        for token in (_align(tokens[index], align)(widths[index]),)
    ])


def project_status_str(
    project: ProjectStatus,
    celt_config: Configuration,
) -> str:
    """Stringify a `ProjectStatus` instance.

    Args:
        project: The `ProjectStatus` instance.
        celt_config: The post processor configuration.

    Returns:
        The string version of the project status.
    """
    keys = project.rules.keys()
    rules = sorted(project.rules.values(), key=cmp_to_key(_compare_rules))

    if project.status == ExitCode.ok:
        buffer = [
            rule_info_str(rule, celt_config)
            for rule in rules
            if rule.ignored
        ]
        if project.total_found > 0:
            buffer.append(
                color(
                    '{gray}project has ',
                    f'{{red}}{project.total_found} errors',
                    '{gray} to clear',
                ),
            )
        else:
            msg = 'no errors found'
            buffer.append(color(f'{{bold_green}}{msg}'))
        return '\n'.join(buffer)

    buffer = [
        rule_info_str(rule, celt_config)
        for rule in rules
        if rule.found > rule.allowed
    ]

    buffer.append(color('{bold}FILES:'))
    by_file = sorted(project.files.items(), key=lambda t: len(t[1]))
    buffer.extend([
        color(f'  {{gray}}{file_name}:{{end}} found {total}')
        for file_name, violations in by_file
        for total in (len(violations), )
    ])
    buffer.append('')

    c1_w = max((len(x) for x in keys))
    c1_w = max([c1_w, len('rules')])
    c2_w = max((len(str(s.found)) for s in rules))
    c2_w = max([c2_w, len('found')])
    c3_w = max((len(str(s.allowed)) for s in rules))
    c3_w = max([c3_w, len('allowed')])
    widths = [c1_w, c2_w, c3_w]

    key_rule = sorted(
        project.rules.items(),
        key=cmp_to_key(_compare_rule_items),
    )
    buffer.append(format_row(['RULES', 'FOUND', 'ALLOWED'], widths, 'lll'))
    buffer.extend([
        (
            color(
                '{gray}',
                format_row([rule_id, rule.found, rule.allowed], widths, 'lrr'),
            )
            if rule.found == rule.allowed
            else format_row([rule_id, rule.found, rule.allowed], widths, 'lrr')
        )
        for rule_id, rule in key_rule
        if not rule.ignored
    ])
    buffer.append('')
    return '\n'.join(buffer)


def project_stats_json(
    name: str,
    project: ProjectStatus,
) -> str:
    """Stringify a `ProjectStatus` instance.

    Displays as json showing the current total of violations for each rule.

    Args:
        name: The name of the compiler/linter.
        project: The `ProjectStatus` instance.

    Returns:
        The string version of the project status.
    """
    cap_name = name.capitalize()
    buffer = [
        '{',
        f'  "allowed{cap_name}Rules": {{',
    ]

    key_rule = sorted(
        [
            x
            for x in project.rules.items()
            if x[1].found > 0 and not x[1].ignored
        ],
        key=cmp_to_key(_compare_rule_items),
    )

    if key_rule:
        buffer.extend([
            f'    "{rule_id}": {rule.found},'
            for rule_id, rule in key_rule[:-1]
        ])
        rule_id, rule = key_rule[-1]
        buffer.append(f'    "{rule_id}": {rule.found}')

    buffer.extend([
        '  }',
        '}',
    ])
    return '\n'.join(buffer)
