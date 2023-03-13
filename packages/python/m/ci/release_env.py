from typing import cast

from m.core import Good, Issue, OneOf, issue, one_of
from m.log import EnvVars
from pydantic import BaseModel

from .config import Config, Workflow
from .git_env import GitEnv


class ReleaseEnv(BaseModel):
    """Object to store the release configuration."""

    build_tag: str
    python_tag: str
    is_release: bool
    is_release_pr: bool
    is_hotfix_pr: bool
    workflow: Workflow


def _verify_version(
    config: Config,
    git_env: GitEnv,
    gh_latest: str,
    is_release_pr: bool,
    is_release: bool,
) -> OneOf[Issue, int]:
    if config.workflow in {Workflow.git_flow, Workflow.m_flow}:
        if config.uses_git_flow():
            pr_branch = git_env.get_pr_branch()
            flow = config.git_flow
            prefixes = (flow.release_prefix, flow.hotfix_prefix)
            # Skip verification when release or hotfix are going to develop
            if git_env.target_branch == flow.develop_branch:
                if pr_branch.startswith(prefixes):
                    return Good(0)
        return config.verify_version(
            gh_latest,
            is_release_pr=is_release_pr,
            is_release=is_release,
        )
    # Covers Workflow.free_flow
    return Good(0)


def _get_develop_branch(config: Config) -> str:
    if config.uses_git_flow():
        return config.git_flow.develop_branch
    return 'develop'


def _extra_checks(
    config: Config,
    git_env: GitEnv,
    is_release_pr: bool,
    is_hotfix_pr: bool,
) -> OneOf[Issue, int]:
    master_branch = config.get_master_branch()
    develop_branch = _get_develop_branch(config)
    valid_branches = (
        (master_branch,)
        if config.uses_m_flow()
        else (master_branch, develop_branch)
    )
    release_pr = is_release_pr or is_hotfix_pr
    if release_pr and git_env.target_branch not in valid_branches:
        error_type = 'release' if is_release_pr else 'hotfix'
        return issue(f'invalid {error_type}-pr', context={
            'expected_target_branch': master_branch,
            'current_target_branch': git_env.target_branch,
            'workflow': str(config.workflow),
        })
    return Good(0)


def get_release_env(
    config: Config,
    env_vars: EnvVars,
    git_env: GitEnv,
) -> OneOf[Issue, ReleaseEnv]:
    """Provide the release environment information.

    Args:
        config: The m configuration.
        env_vars: The environment variables.
        git_env: The git environment.

    Returns:
        A `ReleaseEnv` instance.
    """
    is_release = git_env.is_release(config)
    is_release_pr = git_env.is_release_pr(config)
    is_hotfix_pr = git_env.is_hotfix_pr(config)
    gh_latest = git_env.release.tag_name if git_env.release else ''
    if not config.uses_free_flow():
        check_result = _extra_checks(
            config,
            git_env,
            is_release_pr=is_release_pr,
            is_hotfix_pr=is_hotfix_pr,
        )
        if check_result.is_bad:
            # casting is done since it contains a bad value.
            return cast(OneOf[Issue, ReleaseEnv], check_result)
    return one_of(lambda: [
        ReleaseEnv(
            build_tag=build_tag,
            python_tag=python_tag,
            is_release=is_release,
            is_release_pr=is_release_pr,
            is_hotfix_pr=is_hotfix_pr,
            workflow=config.workflow,
        )
        for _ in _verify_version(
            config,
            git_env,
            gh_latest,
            is_release_pr=is_release_pr or is_hotfix_pr,
            is_release=is_release,
        )
        for build_tag in git_env.get_build_tag(config, env_vars.run_id)
        for python_tag in git_env.get_py_tag(config, env_vars.run_id)
    ])
