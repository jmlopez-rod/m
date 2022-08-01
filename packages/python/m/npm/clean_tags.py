from typing import Dict, List, Set, cast

from ..core import Issue, issue, one_of
from ..core.fp import Good, OneOf
from .cli import get_dist_tags, remove_dist_tag


def clean_tags(pkg: str) -> OneOf[Issue, List[str]]:
    """Remove tags from a package that point to empty versions.

    Args:
        pkg: The name of the npm package.

    Returns:
        A `OneOf` containing a summary of removed tags or an Issue.
    """
    return one_of(lambda: [
        summary
        for tag_map in get_dist_tags(pkg)
        for summary in remove_tags(pkg, find_empty_tags(tag_map))
    ])


def find_empty_tags(tag_map: Dict[str, str]) -> Set[str]:
    """Create a set containing the npm tags that are empty.

    Args:
        tag_map: A dictionary mapping npm tags to versions.

    Returns:
        A set of npm tags that map to empty strings.
    """
    return {
        tag_name
        for tag_name, version in tag_map.items()
        if not version
    }


def remove_tags(pkg: str, tags: Set[str]) -> OneOf[Issue, List[str]]:
    """Call `npm dist-tag` to remove npm tags.

    See https://docs.npmjs.com/cli/v8/commands/npm-dist-tag

    Args:
        pkg: The npm package.
        tags: A set containing the tags to remove.

    Returns:
        A `OneOf` containing a list of the output for each removed tag or an
        issue with a summary.
    """
    issues: List[Issue] = []
    removed: List[str] = []
    for tag in tags:
        cmd_result = remove_dist_tag(pkg, tag)
        if cmd_result.is_bad:
            issues.append(cast(Issue, cmd_result.value))
        else:
            removed.append(cast(str, cmd_result.value))
    if issues:
        return issue('dist-tag rm issues', context={
            'issues': issues,
            'removed': removed,
        })
    return Good(removed)
