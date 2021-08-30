from dataclasses import dataclass
from typing import Optional
from .config import Config, Workflow
from .git_env import GitEnv
from ..core import one_of, issue
from ..core.fp import OneOf, Good
from ..core.issue import Issue
from ..core.io import EnvVars


@dataclass
class ReleaseEnv:
    """Object to store the release configuration."""
    build_tag: str
    is_release: bool
    is_release_pr: bool
    is_hotfix_pr: bool
    workflow: Workflow


def get_release_prefix(config: Config) -> Optional[str]:
    """Find out the release prefix based on the workflow specified in the
    config."""
    if config.workflow == Workflow.GIT_FLOW:
        return config.git_flow.release_prefix
    if config.workflow == Workflow.M_FLOW:
        return config.m_flow.release_prefix
    return None


def get_hotfix_prefix(config: Config) -> Optional[str]:
    """Find out the hotfix prefix based on the workflow specified in the
    config."""
    if config.workflow == Workflow.GIT_FLOW:
        return config.git_flow.hotfix_prefix
    return None


def _verify_version(
    config: Config,
    git_env: GitEnv,
    gh_latest: str,
    is_release_pr: bool,
    is_hotfix_pr: bool,
    is_release: bool
) -> OneOf[Issue, int]:
    if config.workflow == Workflow.GIT_FLOW:
        pr_branch = git_env.get_pr_branch()
        flow = config.git_flow
        # Skip verification only when release or hotfix are going to develop
        if (
            git_env.target_branch == flow.develop_branch and
                (
                    pr_branch.startswith(flow.release_prefix) or
                    pr_branch.startswith(flow.hotfix_prefix)
                )
        ):
            return Good(0)
        return config.verify_version(
            gh_latest,
            is_release_pr=(is_release_pr or is_hotfix_pr),
            is_release=is_release
        )
    if config.workflow == Workflow.M_FLOW:
        return config.verify_version(
            gh_latest,
            is_release_pr=is_release_pr,
            is_release=is_release
        )
    # Covers Workflow.FREE_FLOW
    return Good(0)


def _get_master_branch(config: Config) -> str:
    if config.workflow == Workflow.GIT_FLOW:
        return config.git_flow.master_branch
    if config.workflow == Workflow.M_FLOW:
        return config.m_flow.master_branch
    return 'master'


def _get_develop_branch(config: Config) -> str:
    if config.workflow == Workflow.GIT_FLOW:
        return config.git_flow.develop_branch
    return 'develop'


def get_release_env(
    config: Config,
    env_vars: EnvVars,
    git_env: GitEnv,
) -> OneOf[Issue, ReleaseEnv]:
    """Provide the release environment information."""
    release_prefix = get_release_prefix(config)
    hotfix_prefix = get_hotfix_prefix(config)
    is_release = git_env.is_release(release_prefix, hotfix_prefix)
    is_release_pr = git_env.is_release_pr(release_prefix)
    is_hotfix_pr = git_env.is_hotfix_pr(hotfix_prefix)
    gh_latest = git_env.release.tag_name if git_env.release else ''
    if config.workflow != Workflow.FREE_FLOW:
        master_branch = _get_master_branch(config)
        develop_branch = _get_develop_branch(config)
        if config.workflow == Workflow.GIT_FLOW:
            if (
                (is_release_pr or is_hotfix_pr) and
                git_env.target_branch not in (master_branch, develop_branch)
            ):
                return issue(f'hotfix and releases prs to {master_branch}')
            if (
                is_release and
                git_env.branch not in (master_branch, develop_branch)
            ):
                return issue(f'hotfix and releases only on {master_branch}')
        if config.workflow == Workflow.M_FLOW:
            if (
                is_release_pr and
                git_env.target_branch != master_branch
            ):
                return issue(f'release prs to {master_branch}')
            if (
                is_release and
                git_env.branch != master_branch
            ):
                return issue(f'releases only on {master_branch}')
    return one_of(lambda: [
        ReleaseEnv(
            build_tag=build_tag,
            is_release=is_release,
            is_release_pr=is_release_pr,
            is_hotfix_pr=is_hotfix_pr,
            workflow=config.workflow
        )
        for _ in _verify_version(
            config,
            git_env,
            gh_latest,
            is_release_pr=is_release_pr,
            is_hotfix_pr=is_hotfix_pr,
            is_release=is_release)
        for build_tag in git_env.get_build_tag(
            config,
            env_vars.run_id,
            release_prefix,
            hotfix_prefix)
    ])
