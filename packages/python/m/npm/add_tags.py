from m.ci.docker.tags import docker_tags

from ..core import Issue, issue
from ..core.fp import Bad, Good, OneOf
from .cli import add_dist_tag


def add_tags(pkg: str, version: str) -> OneOf[Issue, list[str]]:
    """Add tags to a package.

    Args:
        pkg: The name of the npm package.
        version: The package version to tag.

    Returns:
        A `OneOf` containing a summary of added tags or an Issue.
    """
    tags = docker_tags(version)
    issues: list[Issue] = []
    added: list[str] = []
    for tag in tags:
        cmd_result = add_dist_tag(pkg, version, tag)
        if isinstance(cmd_result, Bad):
            issues.append(cmd_result.value)
        else:
            added.append(cmd_result.value)
    if issues:
        return issue('dist-tag add issues', context={
            'issues': issues,
            'added': added,
        })
    return Good(added)
