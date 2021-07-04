from dataclasses import dataclass
from typing import List, Mapping, Any
from ..core.fp import OneOf, Good
from ..core.issue import Issue
from ..core import json, one_of, issue


@dataclass
class ReleaseFrom:
    """An object dictating where we are allowed to make a release."""
    pr_branch: str
    allowed_files: List[str]


@dataclass
class Config:
    """Object to store the m project configuration."""
    owner: str
    repo: str
    version: str
    m_dir: str
    release_from: Mapping[str, ReleaseFrom]


def read_release_from(
    data: Mapping[str, Any]
) -> OneOf[Issue, Mapping[str, ReleaseFrom]]:
    """Parse the release-from field. """
    obj = {}
    missing: List[str] = []
    for branch in data:
        item = data[branch]
        if 'prBranch' not in item:
            missing.append(f'{branch}.prBranch')
        if 'allowedFiles' not in item:
            missing.append(f'{branch}.allowedFiles')
        pr_branch = item.get('prBranch', '')
        allowed_files = item.get('allowedFiles', [])
        obj[branch] = ReleaseFrom(pr_branch, allowed_files)
    if missing:
        missing_str = ', '.join(missing)
        return issue(f'missing [{missing_str}] in releaseFrom')
    return Good(obj)


def read_config(m_dir: str) -> OneOf[Issue, Config]:
    """Read an m configuration file."""
    return one_of(lambda: [
        Config(owner, repo, version, m_dir, release_from)
        for data in json.read_json(f'{m_dir}/m.json')
        for owner, repo, version in json.multi_get(
            data, 'owner', 'repo', 'version')
        for release_from in read_release_from(data.get('releaseFrom', {}))
    ]).flat_map_bad(lambda x: issue('read_config failure', cause=x))
