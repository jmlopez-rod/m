from m.ci.docker.tags import docker_tags, is_semver

from ..core import Issue, issue
from ..core.fp import Bad, Good, OneOf
from .cli import add_dist_tag


def add_tags(pkg: str, version: str, branch: str) -> OneOf[Issue, list[str]]:
    """Add tags to a package.

    The branch name will be added to the tags in the event that we have a
    valid sem-version.

    Args:
        pkg: The name of the npm package.
        version: The package version to tag.
        branch: The current branch where the build is taking place.

    Returns:
        A `OneOf` containing a summary of added tags or an Issue.
    """
    tags = docker_tags(version, skip_floating=True)
    if is_semver(version):
        tags.append('latest')
        tags.append(branch)
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
            'issues': [iss.to_dict() for iss in issues],
            'added': added,
        })
    return Good(added)
