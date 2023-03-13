import time

from pydantic import BaseModel

from .config import Config


class VersionInputs(BaseModel):
    """Container with information to generate a version."""

    # '0.0.0-' or 'a.b.c-' or '': Necessary for pr builds
    version_prefix: str

    # the version in the configuration
    version: str

    # unique number for each run in CI environment
    run_id: str | None

    # current commit sha
    sha: str

    pr_number: int | None

    # The build git branch
    branch: str

    is_release: bool
    is_release_pr: bool
    is_hotfix_pr: bool


def build_m_tag(ver_input: VersionInputs, config: Config) -> str:
    """Build an valid "M_TAG".

    Args:
        ver_input: The inputs to create the tag.
        config: The m configuration.

    Returns:
        An m tag that can be used to version npm and docker packages.
    """
    prefix = '' if config.uses_free_flow() else f'{ver_input.version_prefix}-'
    pr_number = ver_input.pr_number
    run_id = ver_input.run_id
    if not run_id:
        return f'{prefix}local.{ver_input.sha}'
    if ver_input.is_release:
        return ver_input.version
    if pr_number:
        nprefix = ''
        if ver_input.is_release_pr:
            nprefix = 'rc'
        elif ver_input.is_hotfix_pr:
            nprefix = 'hotfix'
        if nprefix:
            return f'{ver_input.version}-{nprefix}{pr_number}.b{run_id}'
        return f'{prefix}pr{pr_number}.b{run_id}'
    return f'{prefix}{ver_input.branch}.b{run_id}'


def build_py_tag(ver_input: VersionInputs, config: Config) -> str:
    """Build a valid python version.

    The configuration object is provided since python does not accept using
    names of branches in the versions. For this reason we will map

    Args:
        ver_input: The inputs to create the version.
        config: The m configuration.

    Returns:
        A valid python tag.
    """
    prefix = ver_input.version_prefix
    pr_number = ver_input.pr_number
    run_id = ver_input.run_id
    now = int(time.time())
    if not run_id:
        return f'{prefix}a0+b{now}'
    if ver_input.is_release:
        return ver_input.version
    if pr_number:
        nprefix = ''
        if ver_input.is_release_pr or ver_input.is_hotfix_pr:
            nprefix = 'rc'
        if nprefix:
            return f'{ver_input.version}{nprefix}{pr_number}.dev{run_id}'
        return f'{prefix}b{pr_number}.dev{run_id}'
    nprefix = _get_py_branch_prefix(config, ver_input.branch)
    return f'{prefix}{nprefix}.dev{run_id}'


def _get_py_branch_prefix(config: Config, branch: str) -> str:
    master_branch = config.get_master_branch()
    develop_branch = (
        config.git_flow.develop_branch
        if config.uses_git_flow()
        else 'develop'
    )
    if branch == master_branch:
        return 'rc0'
    if branch == develop_branch:
        return 'b0'
    # letting a0 denote any branch other than the ones for master/develop
    return 'a0'
