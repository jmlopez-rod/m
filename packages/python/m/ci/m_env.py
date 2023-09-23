import json
from pathlib import Path
from typing import Any

from m.core import rw as mio
from m.log import EnvVars, get_ci_tool
from pydantic import BaseModel

from ..core import Res, fp, hone, one_of
from .config import Config, read_config
from .git_env import GitEnv, get_git_env
from .release_env import ReleaseEnv, get_release_env


class MEnv(BaseModel):
    """Contains all the information required for a CI run."""

    config: Config
    env_vars: EnvVars
    git_env: GitEnv
    release_env: ReleaseEnv


def get_m_env(m_dir: str) -> Res[MEnv]:
    """Obtain the M Environment object.

    Args:
        m_dir: The directory containing the m configuration.

    Returns:
        The M Environment if it exists otherwise an issue.
    """
    ci_tool = get_ci_tool()
    return one_of(lambda: [
        MEnv(
            config=config,
            env_vars=env_vars,
            git_env=git_env,
            release_env=release_env,
        )
        for config in read_config(m_dir)
        for env_vars in ci_tool.env_vars()
        for git_env in get_git_env(config, env_vars)
        for release_env in get_release_env(config, env_vars, git_env)
    ]).flat_map_bad(hone('get_m_env failure'))


def _m_env_vars(m_env: MEnv) -> Res[list[str]]:
    """Serialize the m environment variables.

    Args:
        m_env: The `M` environment.

    Returns:
        A string if successful.
    """
    config = m_env.config
    env_vars = m_env.env_vars
    git = m_env.git_env
    release = m_env.release_env
    associated_pr = (
        git.pull_request or (git.commit and git.commit.associated_pull_request)
    )
    associated_pr_num = associated_pr.pr_number if associated_pr else ''
    cache_from_pr = git.get_pr_number() or associated_pr_num
    env = {
        'M_DIR': config.m_dir,
        'M_OWNER': config.owner,
        'M_REPO': config.repo,
        'M_CI': env_vars.ci_env,
        'M_WORKFLOW': config.workflow,
        'M_RUN_ID': env_vars.run_id,
        'M_RUN_NUMBER': env_vars.run_number,
        'M_SHA': git.sha,
        'M_BRANCH': git.branch,
        'M_TARGET_BRANCH': git.target_branch,
        'M_ASSOCIATED_PR_NUMBER': associated_pr_num,
        'M_PR_BRANCH': git.get_pr_branch(),
        'M_PR_NUMBER': git.get_pr_number(),
        'M_TAG': release.build_tag,
        'M_PY_TAG': release.python_tag,
        'M_CACHE_FROM_PR': cache_from_pr,
        'M_IS_RELEASE': release.is_release,
        'M_IS_RELEASE_PR': release.is_release_pr,
        'M_IS_HOTFIX_PR': release.is_hotfix_pr,
    }
    lines = [f'{env_key}={env_val}' for env_key, env_val in env.items()]
    return fp.Good(lines)


def write_m_env_vars(m_dir: str) -> Res[Any]:
    """Write a file with the M environment variables.

    Args:
        m_dir: The directory with the m configuration.

    Returns:
        An issue or the m environment instance.
    """
    target_dir = Path(f'{m_dir}/.m')

    if not Path.exists(target_dir):
        Path.mkdir(target_dir, parents=True)
    return one_of(lambda: [
        json.loads(m_env.model_dump_json())
        for m_env in get_m_env(m_dir)
        for env_list in _m_env_vars(m_env)
        for _ in mio.write_file(f'{m_dir}/.m/env.list', '\n'.join(env_list))
    ])


def _lower_bool(line: str) -> str:
    return line.replace('=False', '=false').replace('=True', '=true')


def bashrc_snippet(m_dir: str) -> Res[str]:
    """Create a bash snippet that exports the M environment variables.

    Args:
        m_dir: The directory with the m configuration.

    Returns:
        An issue or a bash snippet.
    """
    return one_of(lambda: [
        '\n'.join([
            f'export {assignment}'
            for line in env_list
            for assignment in fp.Good(_lower_bool(line))
        ])
        for m_env in get_m_env(m_dir)
        for env_list in _m_env_vars(m_env)
    ])
