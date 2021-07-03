from distutils.version import StrictVersion
from dataclasses import dataclass
from typing import Optional, List, cast
from .config import ReleaseFrom, Config
from .git_env import GitEnv
from ..core.fp import Good, OneOf
from ..core.issue import Issue, issue
from ..core.io import EnvVars


@dataclass
class ReleaseEnv:
    """Object to store the release configuration."""
    version: str
    is_release: bool
    is_release_pr: bool
    release_from: Optional[ReleaseFrom]


def _found(ver: str, res: ReleaseEnv) -> OneOf[Issue, ReleaseEnv]:
    res.version = ver
    return Good(res)


def _verify_version(
    ver: str,
    gh_latest: str,
    is_release_pr: bool,
    is_release: bool
) -> OneOf[Issue, None]:
    """Helper function to stop the flow in case the version was improperly
    modified."""
    if gh_latest:
        try:
            p_ver = StrictVersion(ver)
            p_latest = StrictVersion(gh_latest)
            ver_gt_latest = p_ver > p_latest
            ver_lt_latest = p_ver < p_latest
        except Exception as ex:
            return issue(
                'error comparing versions',
                cause=ex,
                data=dict(current_version=ver, gh_latest=gh_latest))
        if is_release_pr and not ver_gt_latest:
            return issue(
                f'version needs to be greater than {gh_latest}',
                data=dict(version=ver))
        if not is_release_pr and not is_release:
            if ver_lt_latest:
                return issue(
                    f'version is behind {gh_latest}. Merge latest?',
                    data=dict(version=ver))
            if ver_gt_latest:
                return issue(
                    f'version is ahead {gh_latest}. Revert the change.',
                    data=dict(version=ver))
    return Good(None)


def _verify_pr(
    git_env: GitEnv,
    run_id: str,
    is_release_pr: bool,
    release_from: Optional[ReleaseFrom],
    result: ReleaseEnv,
) -> OneOf[Issue, Optional[ReleaseEnv]]:
    if git_env.pull_request:
        pr = git_env.pull_request
        if is_release_pr:
            allowed_files: List[str] = []
            if release_from:
                allowed_files = release_from.allowed_files
            if allowed_files and pr.file_count > len(allowed_files):
                return issue(
                    'max files threshold exceeded in release pr',
                    data=dict(
                        allowed_files=allowed_files,
                        file_count=pr.file_count))
            if allowed_files and not set(pr.files).issubset(set(allowed_files)):
                return issue(
                    'modified files not subset of the allowed files.',
                    data=dict(
                        modified_fles=pr.files,
                        allowed_files=allowed_files))
        pr_num = pr.pr_number
        result.version = f'0.0.0-pr{pr_num}.b{run_id}'
        return Good(result)
    return Good(None)


def get_release_env(
    config: Config,
    env_vars: EnvVars,
    git_env: GitEnv,
) -> OneOf[Issue, ReleaseEnv]:
    """Provide the release environment information."""
    release_from = config.release_from.get(git_env.target_branch)
    is_release = git_env.is_release(release_from)
    is_release_pr = git_env.is_release_pr(release_from)
    result = ReleaseEnv(
        version='',
        is_release=is_release,
        is_release_pr=is_release_pr,
        release_from=release_from
    )

    sha = git_env.sha
    ver = config.version
    target_branch = git_env.target_branch

    gh_latest = git_env.release.tag_name if git_env.release else ''
    _g1 = _verify_version(ver, gh_latest, is_release_pr, is_release)
    if _g1.is_bad:
        return cast(OneOf[Issue, ReleaseEnv], _g1)

    if not env_vars.ci_env:
        return _found(f'0.0.0-local.{sha}', result)

    _g2 = _verify_pr(
        git_env=git_env,
        run_id=env_vars.run_id,
        is_release_pr=is_release_pr,
        release_from=release_from,
        result=result
    )
    if _g2.is_bad or _g2.value:
        return cast(OneOf[Issue, ReleaseEnv], _g2)

    if is_release:
        return _found(ver, result)

    return _found(f'0.0.0-{target_branch}.b{env_vars.run_id}', result)
