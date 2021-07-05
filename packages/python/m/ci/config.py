from distutils.version import StrictVersion
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
    required_files: List[str]


@dataclass
class Config:
    """Object to store the m project configuration."""
    owner: str
    repo: str
    version: str
    m_dir: str
    release_from_dict: Mapping[str, ReleaseFrom]

    def verify_version(
        self,
        gh_latest: str,
        is_release_pr: bool,
        is_release: bool,
    ) -> OneOf[Issue, int]:
        """Return 0 if everything is well with the version in the
        configuration. Otherwise it will return an issue stating why
        the version in the configuration is not valid. If `gh_latest`
        is not provided then the checks are skipped."""
        if not gh_latest:
            return Good(0)
        err_data = dict(
            config_version=self.version,
            gh_latest=gh_latest,
            is_release=is_release,
            is_release_pr=is_release_pr,
        )
        try:
            p_ver = StrictVersion(self.version)
            p_latest = StrictVersion(gh_latest)
            ver_gt_latest = p_ver > p_latest
            ver_lt_latest = p_ver < p_latest
        except Exception as ex:
            return issue('error comparing versions', cause=ex, data=err_data)
        msg: str = ''
        if is_release_pr:
            if not ver_gt_latest:
                msg = 'version needs to be bumped'
        elif not is_release:
            if ver_lt_latest:
                msg = 'version is behind (Branch may need to be updated)'
            elif ver_gt_latest:
                msg = 'version is ahead (Revert configuration change)'
        elif is_release:
            if not ver_gt_latest:
                msg = 'version was not bumped during release pr'
        if msg:
            return issue(msg, data=err_data)
        return Good(0)


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
        pr_branch = item.get('prBranch', '')
        allowed_files = item.get('allowedFiles', [])
        required_files = item.get('requiredFiles', [])
        obj[branch] = ReleaseFrom(pr_branch, allowed_files, required_files)
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
