from dataclasses import dataclass
from typing import Optional
from .config import Config, Workflow
from .git_env import GitEnv
from ..core import one_of
from ..core.fp import OneOf
from ..core.issue import Issue
from ..core.io import EnvVars


@dataclass
class ReleaseEnv:
    """Object to store the release configuration."""
    build_tag: str
    is_release: bool
    is_release_pr: bool
    workflow: Workflow


def get_release_prefix(config: Config) -> Optional[str]:
    """Find out the release prefix based on the workflow specified in the
    config."""
    if config.workflow == Workflow.GIT_FLOW:
        return config.git_flow.release_prefix
    if config.workflow == Workflow.M_FLOW:
        return config.m_flow.release_prefix
    if config.workflow == Workflow.FREE_FLOW:
        return None
    return None


def get_release_env(
    config: Config,
    env_vars: EnvVars,
    git_env: GitEnv,
) -> OneOf[Issue, ReleaseEnv]:
    """Provide the release environment information."""
    workflow = config.workflow
    release_prefix = get_release_prefix(config)
    is_release = git_env.is_release(release_prefix)
    is_release_pr = git_env.is_release_pr(release_prefix)
    gh_latest = git_env.release.tag_name if git_env.release else ''
    return one_of(lambda: [
        ReleaseEnv(
            build_tag=build_tag,
            is_release=is_release,
            is_release_pr=is_release_pr,
            workflow=workflow
        )
        for _ in config.verify_version(
            gh_latest,
            is_release_pr=is_release_pr,
            is_release=is_release)
        for build_tag in git_env.get_build_tag(
            config.version,
            env_vars.run_id,
            release_prefix)
    ])
