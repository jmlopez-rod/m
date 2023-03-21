import re
from typing import Any, Dict, List, Optional, Tuple

from ....core import Good, Issue, OneOf, issue, one_of
from .io import project_stats_json, project_status_str
from .types import (
    Configuration,
    ExitCode,
    FileReport,
    ProjectStatus,
    RuleInfo,
    Transform,
    Violation,
)


def replace_filenames(
    payload: str,
    file_prefix: Optional[str],
) -> OneOf[Issue, str]:
    """Replace the prefix of file names.

    Args:
        payload: str
            The payload from a compiler/linter.
        file_prefix: Optional[str]
            A string of the form `[old]:[new]`. The old prefix can be
            a `|` separated list of strings. For instance
            `path/to/foo|path/to:bar`

    Returns:
        A `OneOf` containing an Issue or the `payload` with all file path
        replaced according to the file_prefix.
    """
    if not file_prefix:
        return Good(payload)
    try:
        old, prefix = file_prefix.split(':')
    except ValueError as ex:
        return issue('file_prefix param missing `:`', cause=ex)
    return Good(re.sub(
        fr'({old})(.*?)\.([a-z]+)',
        lambda x: [
            # Not sure how fix this mypy issue
            f'{prefix}{filename}.{ext}'  # type: ignore
            for _, filename, ext in (x.groups(),)
        ][0],
        payload,
    ))


def filter_reports(
    reports: List[FileReport],
    regex: Optional[str] = None,
) -> List[FileReport]:
    """Filter the list of file reports based on the file path.

    It also removes any file report that does not have any violations.

    Args:
        reports: List of file reports.
        regex: The post processor configuration.

    Returns:
        A list of file reports with at least one violation and file_path
        matching the provided regex.
    """
    return [
        rpt
        for rpt in reports
        if rpt.violations and (not regex or re.match(regex, rpt.file_path))
    ]


def to_rules_dict(reports: List[FileReport]) -> Dict[str, List[Violation]]:
    """Convert a list of `FileReport` to a map of rules to `Violation`.

    Args:
        reports: A list of `FileReport` instances.

    Returns:
        A dictionary mapping rules to a list of `Violation`.
    """
    rules: Dict[str, List[Violation]] = {}
    for report in reports:
        for violation in report.violations:
            if violation.rule_id not in rules:
                rules[violation.rule_id] = []
            rules[violation.rule_id].append(violation)
    return rules


def _process_rules_dict(
    rules_dict: Dict[str, List[Violation]],
    allowed_rules: Dict[str, int],
    ignored_rules: Dict[str, str],
    rules: Dict[str, RuleInfo],
) -> Tuple[bool, bool]:
    """Populate the `rules` dictionary.

    It is meant to be used in the `get_project_status` function.

    Args:
        rules_dict: A map of rule ids to a list of violations.
        allowed_rules: A dictionary specifying the allowed violations.
        ignored_rules: A dictionary specified the rules to ignore.
        rules: An empty dictionary created in `get_project_status`.

    Returns:
        The preliminary values for failed and needs_readjustment.
    """
    failed = False
    needs_readjustment = False

    for rule_id, violations in rules_dict.items():
        total_violations = len(violations)
        allowed = allowed_rules.get(rule_id, 0)
        ignored = bool(ignored_rules.get(rule_id))
        if not ignored:
            if total_violations > allowed:
                failed = True
            elif total_violations < allowed:
                needs_readjustment = True
        rules[rule_id] = RuleInfo(
            rule_id,
            violations,
            total_violations,
            allowed,
            ignored,
        )
    return failed, needs_readjustment


def get_project_status(
    payload: str,
    reports: List[FileReport],
    rules_dict: Dict[str, List[Violation]],
    allowed_rules: Dict[str, int],
    ignored_rules: Dict[str, str],
) -> ProjectStatus:
    """Analyze the rules_dictionary with the allowed and ignored rules.

    Args:
        payload: The original payload from the compiler/linter.
        reports: List of file reports.
        rules_dict: A map of rule ids to a list of violations.
        allowed_rules: A dictionary specifying the allowed violations.
        ignored_rules: A dictionary specifying the rules to ignore.

    Returns:
        A ProjectStatus object.
    """
    rules: Dict[str, RuleInfo] = {}
    files: Dict[str, List[Violation]] = {
        x.file_path: x.violations
        for x in reports
    }

    failed, needs_readjustment = _process_rules_dict(
        rules_dict, allowed_rules, ignored_rules, rules,
    )

    for rule_id, allowed in allowed_rules.items():
        if rule_id not in rules:
            rules[rule_id] = RuleInfo(rule_id, [], 0, allowed, ignored=False)
            if allowed > 0:
                needs_readjustment = True

    status = ExitCode.ok
    if failed:
        status = ExitCode.error
    elif needs_readjustment:
        status = ExitCode.needs_readjustment
    return ProjectStatus(status, payload, rules, files)


def process(
    raw_payload: str,
    transform: Transform,
    allowed_rules: Dict[str, int],
    ignored_rules: Dict[str, str],
    celt_config: Configuration,
) -> OneOf[Issue, ProjectStatus]:
    """Process the output of a compiler/linter.

    Args:
        raw_payload: The payload from the compiler/linter.
        transform: Function to generate a list of `FileReport` objects.
        allowed_rules: A dictionary specifying the allowed violations.
        ignored_rules: A dictionary specifying the rules to ignore.
        celt_config: The post processor configuration.

    Returns:
        A `OneOf` containing an `Issue` or a `ProjectStatus` object.
    """
    return one_of(lambda: [
        project_status
        for payload in replace_filenames(raw_payload, celt_config.file_prefix)
        for reports in transform(payload)
        for filtered in (filter_reports(reports, celt_config.file_regex),)
        for rules_dict in (to_rules_dict(filtered),)
        for project_status in (
            get_project_status(
                payload, filtered, rules_dict, allowed_rules, ignored_rules,
            ),
        )
    ])


class PostProcessor:
    """A post processor to handle a compiler/linter ouput."""

    def __init__(
        self,
        name: str,
        celt_config: Configuration,
        transform: Transform,
    ):
        """Instantiate a `PostProcessor`.

        Args:
            name: The name of the compiler/linter.
            celt_config: The post processor configuration.
            transform: Function to generate a list of `FileReport` objects.
        """
        self.name = name
        self.celt_config = celt_config
        self.transform = transform

    def run(
        self,
        payload: str,
        config: Dict[str, Any],
    ) -> OneOf[Issue, ProjectStatus]:
        """Run the processor on the given payload.

        Args:
            payload: The payload from the compiler/linter.
            config: A dictionary with rule allowance/ignores.

        Returns:
            A `OneOf` containing an `Issue` or the `ProjectStatus`.
        """
        cap_name = self.name.capitalize()
        allowed_rules = config.get(f'allowed{cap_name}Rules', {})
        if self.celt_config.ignore_error_allowance:
            allowed_rules = {}
        ignored_rules = config.get(f'ignored{cap_name}Rules', {})
        return process(
            payload,
            self.transform,
            allowed_rules,
            ignored_rules,
            self.celt_config,
        )

    def to_str(self, project: ProjectStatus) -> str:
        """Stringify a `ProjectStatus`.

        Args:
            project: The `ProjectStatus` obtained by running the `run` method.

        Returns:
            The string version of the project status.
        """
        return project_status_str(project, self.celt_config)

    def stats_json(self, project: ProjectStatus) -> str:
        """Stringify a `ProjectStatus`.

        Show a dictionary with the total number of violations. Useful when
        writing an entry for the configuration file.

        Args:
            project: The `ProjectStatus` obtained by running the `run` method.

        Returns:
            The string version of the project status.
        """
        return project_stats_json(self.name, project)
