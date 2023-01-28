from typing import cast

from m.core.ci_tools import EnvVars
from pydantic import BaseModel

from ..core import issue, one_of
from ..core.fp import Good, OneOf
from ..core.issue import Issue
from .config import Config, Workflow
from .git_env import GitEnv


class ReleaseEnv(BaseModel):
    """Object to store the release configuration."""

    build_tag: str
    is_release: bool
    is_release_pr: bool
    is_hotfix_pr: bool
    workflow: Workflow


def _verify_version(
    config: Config,
    git_env: GitEnv,
    gh_latest: str,
    is_release_pr: bool,
    is_hotfix_pr: bool,
    is_release: bool,
) -> OneOf[Issue, int]:
    if config.workflow in [Workflow.git_flow, Workflow.m_flow]:
        if config.uses_git_flow():
            pr_branch = git_env.get_pr_branch()
            flow = config.git_flow
            # Skip verification when release or hotfix are going to develop
            if git_env.target_branch == flow.develop_branch:
                if (
                    pr_branch.startswith(flow.release_prefix) or
                    pr_branch.startswith(flow.hotfix_prefix)
                ):
                    return Good(0)
        return config.verify_version(
            gh_latest,
            is_release_pr=(is_release_pr or is_hotfix_pr),
            is_release=is_release,
        )
    # Covers Workflow.free_flow
    return Good(0)


def _get_master_branch(config: Config) -> str:
    # to be used if not using the free flow
    if config.uses_git_flow():
        return config.git_flow.master_branch
    return config.m_flow.master_branch


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
    master_branch = _get_master_branch(config)
    develop_branch = _get_develop_branch(config)
    if config.uses_git_flow():
        if (
            (is_release_pr or is_hotfix_pr) and
            git_env.target_branch not in (master_branch, develop_branch)
        ):
            error_type = 'release' if is_release_pr else 'hotfix'
            return issue(f'invalid {error_type}-pr', data={
                'expected_target_branch': master_branch,
                'current_target_branch': git_env.target_branch,
                'workflow': str(config.workflow),
            })
        # is_release implies git_env.branch == master_branch
    if config.uses_m_flow():
        if (
            (is_release_pr or is_hotfix_pr) and
            git_env.target_branch != master_branch
        ):
            error_type = 'release' if is_release_pr else 'hotfix'
            return issue(f'invalid {error_type}-pr', data={
                'expected_target_branch': master_branch,
                'current_target_branch': git_env.target_branch,
                'workflow': str(config.workflow),
            })
        # is_release being true implies git_env.branch == master_branch
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
            is_release=is_release,
            is_release_pr=is_release_pr,
            is_hotfix_pr=is_hotfix_pr,
            workflow=config.workflow,
        )
        for _ in _verify_version(
            config,
            git_env,
            gh_latest,
            is_release_pr=is_release_pr,
            is_hotfix_pr=is_hotfix_pr,
            is_release=is_release)
        for build_tag in git_env.get_build_tag(config, env_vars.run_id)
    ])
