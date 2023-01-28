from pydantic import BaseModel


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


def build_m_tag(ver_input: VersionInputs) -> str:
    """Build an valid "M_TAG".

    Args:
        ver_input: The inputs to create the tag.

    Returns:
        An m tag that can be used to version npm and docker packages.
    """
    prefix = ver_input.version_prefix
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
