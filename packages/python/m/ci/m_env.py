import os
from dataclasses import dataclass
from typing import Any, cast

from ..core import Issue, fp, issue, one_of
from ..core.io import CiTool, EnvVars, JsonStr, write_file
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
    """Obtain the M Environment object."""
    return one_of(lambda: [
        MEnv(config, env_vars, git_env, release_env)
        for config in read_config(m_dir)
        for env_vars in CiTool.env_vars()
        for git_env in get_git_env(config, env_vars)
        for release_env in get_release_env(config, env_vars, git_env)
    ]).flat_map_bad(lambda x: issue('get_m_env failure', cause=cast(Issue, x)))


def _m_env_vars(m_env: MEnv) -> fp.OneOf[Issue, str]:
    """Serialize the m environment variables."""
    config = m_env.config
    env_vars = m_env.env_vars
    git = m_env.git_env
    release = m_env.release_env
    associated_pr = (
        git.pull_request or (git.commit and git.commit.associated_pull_request)
    )
    associated_pr_num = associated_pr.pr_number if associated_pr else ''
    env = {
        'M_DIR': config.m_dir,
        'M_OWNER': config.owner,
        'M_REPO': config.repo,
        'M_CI': env_vars.ci_env,
        'M_WORKFLOW': config.workflow.value,
        'M_RUN_ID': env_vars.run_id,
        'M_RUN_NUMBER': env_vars.run_number,
        'M_SHA': git.sha,
        'M_BRANCH': git.branch,
        'M_TARGET_BRANCH': git.target_branch,
        'M_ASSOCIATED_PR_NUMBER': associated_pr_num,
        'M_PR_BRANCH': git.get_pr_branch(),
        'M_PR_NUMBER': git.get_pr_number(),
        'M_TAG': release.build_tag,
        'M_IS_RELEASE': release.is_release,
        'M_IS_RELEASE_PR': release.is_release_pr,
        'M_IS_HOTFIX_PR': release.is_hotfix_pr,
    }
    return fp.Good('\n'.join([f'{key}={val}' for key, val in env.items()]))


def write_m_env_vars(m_dir: str) -> fp.OneOf[Issue, Any]:
    """Write a file with the M environment variables."""
    target_dir = f'{m_dir}/.m'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return one_of(lambda: [
        m_env
        for m_env in get_m_env(m_dir)
        for env_list in _m_env_vars(m_env)
        for _ in write_file(f'{m_dir}/.m/env.list', env_list)
    ])
