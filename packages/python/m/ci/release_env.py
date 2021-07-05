from dataclasses import dataclass
from typing import Optional
from .config import ReleaseFrom, Config
from .git_env import GitEnv
from ..core import one_of
from ..core.fp import OneOf
from ..core.issue import Issue
from ..core.io import EnvVars


@dataclass
class ReleaseEnv:
    """Object to store the release configuration."""
    version: str
    is_release: bool
    is_release_pr: bool
    release_from: Optional[ReleaseFrom]


def get_release_env(
    config: Config,
    env_vars: EnvVars,
    git_env: GitEnv,
) -> OneOf[Issue, ReleaseEnv]:
    """Provide the release environment information."""
    release_from = config.release_from_dict.get(git_env.target_branch)
    is_release = git_env.is_release(release_from)
    is_release_pr = git_env.is_release_pr(release_from)

    gh_latest = git_env.release.tag_name if git_env.release else ''
    return one_of(lambda: [
        ReleaseEnv(
            version=build_tag,
            is_release=is_release,
            is_release_pr=is_release_pr,
            release_from=release_from
        )
        for _ in config.verify_version(
            gh_latest,
            is_release_pr=is_release_pr,
            is_release=is_release)
        for _ in git_env.verify_release_pr(release_from)
        for build_tag in git_env.get_build_tag(
            config.version,
            env_vars.run_id,
            release_from)
    ])
