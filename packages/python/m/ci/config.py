from distutils.version import StrictVersion
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Any
from ..core.fp import OneOf, Good
from ..core.issue import Issue
from ..core import json, one_of, issue


class Workflow(Enum):
    """Supported workflows."""
    GIT_FLOW = 'git_flow'
    M_FLOW = 'm_flow'
    FREE_FLOW = 'free_flow'


@dataclass
class GitFlowConfig:
    """An object mapping branches for the git_flow workflow."""
    master_branch: str
    develop_branch: str
    release_prefix: str
    hotfix_prefix: str


@dataclass
class MFlowConfig:
    """An object mapping branches for the m_flow workflow."""
    master_branch: str
    release_prefix: str


@dataclass
class Config:
    """Object to store the m project configuration."""
    owner: str
    repo: str
    version: str
    m_dir: str
    workflow: Workflow
    git_flow: GitFlowConfig
    m_flow: MFlowConfig

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


def read_workflow(data: str) -> OneOf[Issue, Workflow]:
    """Parse the workflow field."""
    try:
        name = data.upper().replace('-', '_')
        return Good(Workflow[name])
    except Exception as ex:
        return issue('invalid workflow', cause=ex)


def read_git_flow(data: Mapping[str, Any]) -> OneOf[Issue, GitFlowConfig]:
    """Parse the gitFlow field."""
    config = GitFlowConfig(
        master_branch=data.get('masterBranch', 'master'),
        develop_branch=data.get('developBranch', 'develop'),
        release_prefix=data.get('releasePrefix', 'release'),
        hotfix_prefix=data.get('hotfixPrefix', 'hotfix'),
    )
    return Good(config)


def read_m_flow(data: Mapping[str, Any]) -> OneOf[Issue, MFlowConfig]:
    """Parse the mFlow field."""
    config = MFlowConfig(
        master_branch=data.get('masterBranch', 'master'),
        release_prefix=data.get('releasePrefix', 'release'),
    )
    return Good(config)


def read_config(m_dir: str) -> OneOf[Issue, Config]:
    """Read an m configuration file."""
    return one_of(lambda: [
        Config(owner, repo, version, m_dir, workflow, git_flow, m_flow)
        for data in json.read_json(f'{m_dir}/m.json')
        for owner, repo, version in json.multi_get(
            data, 'owner', 'repo', 'version')
        for workflow in read_workflow(data.get('workflow', 'free-flow'))
        for git_flow in read_git_flow(data.get('gitFlow', {}))
        for m_flow in read_m_flow(data.get('mFlow', {}))
    ]).flat_map_bad(lambda x: issue('read_config failure', cause=x))
