import os
from dataclasses import dataclass
from typing import cast
from ..core import fp, issue, one_of
from ..core.issue import Issue
from ..core.io import EnvVars, CiTool, write_file, JsonStr
from .config import Config, read_config
from .git_env import GitEnv, get_git_env
from .release_env import ReleaseEnv, get_release_env


@dataclass
class MEnv(JsonStr):
    """Contains all the information required for a CI run."""
    config: Config
    env_vars: EnvVars
    git_env: GitEnv
    release_env: ReleaseEnv


def get_m_env(m_dir: str) -> fp.OneOf[Issue, MEnv]:
    """Obtain the M Environment object"""
    return one_of(lambda: [
        MEnv(config, env_vars, git_env, release_env)
        for config in read_config(m_dir)
        for env_vars in CiTool.env_vars().flat_map_bad(
            lambda x: issue('env_vars failure', cause=x)
        )
        for git_env in get_git_env(
            config,
            env_vars
        ).flat_map_bad(lambda x: issue('git_env failure', cause=x))
        for release_env in get_release_env(
            config,
            env_vars,
            git_env
        ).flat_map_bad(lambda x: issue('release_env failure', cause=x))
    ]).flat_map_bad(lambda x: issue('get_m_env failure', cause=cast(Issue, x)))


def _m_env_vars(m_env: MEnv) -> fp.OneOf[Issue, str]:
    """Serialize the m environment variables."""
    config = m_env.config
    env_vars = m_env.env_vars
    git = m_env.git_env
    release = m_env.release_env
    associated_pr = (
        git.pull_request
        or (git.commit and git.commit.associated_pull_request)
    )
    env = dict(
        M_DIR=config.m_dir,
        M_OWNER=config.owner,
        M_REPO=config.repo,
        M_CI=env_vars.ci_env,
        M_RUN_ID=env_vars.run_id,
        M_RUN_NUMBER=env_vars.run_number,
        M_SHA=git.sha,
        M_BRANCH=git.branch,
        M_TARGET_BRANCH=git.target_branch,
        M_ASSOCIATED_PR_NUMBER=associated_pr and associated_pr.pr_number or '',
        M_PR_BRANCH=git.get_pr_branch(),
        M_PR_NUMBER=git.get_pr_number(),
        M_TAG=release.build_tag,
        M_IS_RELEASE=release.is_release,
        M_IS_RELEASE_PR=release.is_release_pr,
    )
    print(str(m_env))
    return fp.Good('\n'.join([f'{key}={val}' for key, val in env.items()]))


def write_m_env_vars(m_dir: str) -> fp.OneOf[Issue, int]:
    """Write a file with the M environment variables."""
    target_dir = f'{m_dir}/.m'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return one_of(lambda: [
        0
        for m_env in get_m_env(m_dir)
        for contents in _m_env_vars(m_env)
        for _ in write_file(f'{m_dir}/.m/env.list', contents)
    ]).flat_map_bad(
        lambda x: issue('write_m_env failure', cause=cast(Issue, x)))
