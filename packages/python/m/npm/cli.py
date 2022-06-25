from typing import Dict

from ..core import one_of, subprocess
from ..core.fp import OneOf
from ..core.issue import Issue
from ..core.json import parse_json


def get_dist_tags(pkg_name: str) -> OneOf[Issue, Dict[str, str]]:
    """Fetch all the npm tags for a package.

    Args:
        pkg_name: The name of the npm package.

    Returns:
        A `OneOf` containing an `Issue` or map specifying the tags to a
        published version.
    """
    cmd = f'npm info {pkg_name} dist-tags --json'
    return one_of(lambda: [
        tag_map
        for payload in subprocess.eval_cmd(cmd)
        for tag_map in parse_json(payload)
    ])


def remove_dist_tag(pkg_name: str, tag: str) -> OneOf[Issue, str]:
    """Remove an npm tag.

    Args:
        pkg_name: The name of the npm package.
        tag: The tag to remove.

    Returns:
        A `OneOf` containing an `Issue` or the output of the npm command.
    """
    return subprocess.eval_cmd(f'npm dist-tag rm {pkg_name} {tag} --json')
