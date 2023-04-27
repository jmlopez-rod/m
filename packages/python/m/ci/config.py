from pathlib import Path

from packaging.version import Version
from pydantic import BaseModel

from ..core import Good, Issue, OneOf, issue, one_of, yaml_fp
from .types import Branches, GitFlowConfig, MFlowConfig, Workflow


def _handle_release_pr(ver_gt_latest: bool) -> str:
    return '' if ver_gt_latest else 'version needs to be bumped'


def _handle_release(ver_gt_latest: bool) -> str:
    return '' if ver_gt_latest else 'version was not bumped during release pr'


def _handle_non_release(ver_lt_latest: bool, ver_gt_latest: bool) -> str:
    if ver_lt_latest:
        return 'version is behind (Branch may need to be updated)'
    if ver_gt_latest:
        return 'version is ahead (Revert configuration change)'
    return ''


class Config(BaseModel):
    """Object to store the m project configuration."""

    # pylint: disable=too-many-instance-attributes
    m_dir: str
    owner: str
    repo: str
    version: str = '0.0.0'
    workflow: Workflow = Workflow.free_flow
    git_flow: GitFlowConfig = GitFlowConfig(
        master_branch=Branches.master,
        develop_branch=Branches.develop,
        release_prefix=Branches.release,
        hotfix_prefix=Branches.hotfix,
    )
    m_flow: MFlowConfig = MFlowConfig(
        master_branch=Branches.master,
        release_prefix=Branches.release,
        hotfix_prefix=Branches.hotfix,
    )
    build_tag_with_version: bool = False

    class Config:
        """Config to allow enums to be displayed as strings."""

        use_enum_values = True

    def uses_git_flow(self):
        """Check if configuration is using the git flow.

        Returns:
            True if workflow is the git flow.
        """
        return self.workflow == Workflow.git_flow

    def uses_m_flow(self):
        """Check if configuration is using the m flow.

        Returns:
            True if workflow is the m flow.
        """
        return self.workflow == Workflow.m_flow

    def uses_free_flow(self):
        """Check if configuration is using the free flow.

        Returns:
            True if workflow is the free flow.
        """
        return self.workflow == Workflow.free_flow

    def get_master_branch(self) -> str:
        """Obtain the name of the branch that aliases the "master" branch.

        Returns:
            The name/alias assigned to the `master` branch.
        """
        if self.uses_m_flow():
            return self.m_flow.master_branch
        if self.uses_git_flow():
            return self.git_flow.master_branch
        return 'master'

    def get_develop_branch(self) -> str:
        """Obtain the name of the branch that aliases the "develop" branch.

        Returns:
            The name/alias assigned to the `develop` branch.
        """
        if self.uses_git_flow():
            return self.git_flow.develop_branch
        return 'develop'

    def get_default_branch(self) -> str:
        """Obtain the name of the branch that aliases the "default" branch.

        This is dependent on the flow. For instance, in the git flow we
        use the `develop` branch as default.

        Returns:
            The name/alias assigned to the default branch.
        """
        if self.uses_m_flow():
            return self.m_flow.master_branch
        if self.uses_git_flow():
            return self.git_flow.develop_branch
        return 'master'

    def verify_version(
        self,
        gh_latest: str,
        is_release_pr: bool,
        is_release: bool,
    ) -> OneOf[Issue, int]:
        """Verify that the configuration version is valid.

        Args:
            gh_latest:
                The version stored in `Github`. Checks are skipped if
                this value is empty.
            is_release_pr:
                Set to `True` if the build is done during a release pr.
            is_release:
                Set to `True` if the build is done during a release.

        Returns:
            A `OneOf` containing 0 if all is well, otherwise an `Issue`.
        """
        if not gh_latest:
            return Good(0)
        err_data = {
            'config_version': self.version,
            'gh_latest': gh_latest,
            'is_release': is_release,
            'is_release_pr': is_release_pr,
        }
        try:
            p_ver = Version(self.version)
        except Exception as ex:
            return issue('error parsing version', cause=ex, context=err_data)
        try:
            p_latest = Version(gh_latest)
        except Exception as ex:  # noqa: WPS440
            return issue('error parsing latest', cause=ex, context=err_data)
        ver_gt_latest = p_ver > p_latest
        ver_lt_latest = p_ver < p_latest
        msg: str = ''
        if is_release_pr:
            msg = _handle_release_pr(ver_gt_latest)
        elif is_release:
            msg = _handle_release(ver_gt_latest)
        else:
            msg = _handle_non_release(ver_lt_latest, ver_gt_latest)
        return issue(msg, context=err_data) if msg else Good(0)


def get_m_filename(m_dir: str) -> OneOf[Issue, str]:
    """Obtain the path to the m configuration file.

    Args:
        m_dir: The directory with the m configuration.

    Returns:
        The name of the configuration file or an issue if it doesn't exist.
    """
    filenames = (f'{m_dir}/m.yaml', f'{m_dir}/m.yml', f'{m_dir}/m.json')
    for filename in filenames:
        if Path(filename).exists():
            return Good(filename)
    return issue('m_file not found', context={
        'm_dir': m_dir,
        'valid_m_files': filenames,
    })


def read_config(m_dir: str) -> OneOf[Issue, Config]:
    """Read an m configuration file.

    Args:
        m_dir: Directory containing `m.json`.

    Returns:
        A `OneOf` containing the `m` configuration or an `Issue`.
    """
    return one_of(lambda: [
        Config(m_dir=m_dir, **m_cfg)
        for m_filename in get_m_filename(m_dir)
        for m_cfg in yaml_fp.read_yson(m_filename)
    ]).flat_map_bad(lambda x: issue('read_config failure', cause=x))
