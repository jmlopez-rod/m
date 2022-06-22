from dataclasses import dataclass
from distutils.version import StrictVersion

from ..core import Good, Issue, OneOf, issue, json, one_of
from ..core.io import JsonStr
from .types import (
    GitFlowConfig,
    MFlowConfig,
    Workflow,
    read_git_flow,
    read_m_flow,
    read_workflow,
)


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


@dataclass
class Config(JsonStr):
    """Object to store the m project configuration."""

    # pylint: disable=too-many-instance-attributes
    owner: str
    repo: str
    version: str
    m_dir: str
    workflow: Workflow
    git_flow: GitFlowConfig
    m_flow: MFlowConfig
    build_tag_with_version: bool = False

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
            p_ver = StrictVersion(self.version)
        except Exception as ex:
            return issue('error parsing version', cause=ex, context=err_data)
        try:
            p_latest = StrictVersion(gh_latest)
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


def read_config(m_dir: str) -> OneOf[Issue, Config]:
    """Read an m configuration file.

    Args:
        m_dir: Directory containing `m.json`.

    Returns:
        A `OneOf` containing the `m` configuration or an `Issue`.
    """
    return one_of(lambda: [
        Config(
            owner,
            repo,
            version,
            m_dir,
            workflow,
            git_flow,
            m_flow,
            build_tag_with_version=with_version,
        )
        for m_cfg in json.read_json(f'{m_dir}/m.json')
        for owner, repo in json.multi_get(m_cfg, 'owner', 'repo')
        for version in (m_cfg.get('version', '0.0.0'),)
        for workflow in read_workflow(m_cfg.get('workflow', 'free-flow'))
        for git_flow in read_git_flow(m_cfg.get('gitFlow', {}))
        for m_flow in read_m_flow(m_cfg.get('mFlow', {}))
        for with_version in (m_cfg.get('build_tag_with_version', False),)
    ]).flat_map_bad(lambda x: issue('read_config failure', cause=x))
