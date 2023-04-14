from enum import Enum

from pydantic import BaseModel


class Branches(str, Enum):  # noqa: WPS600
    """Default branches to use for the supported workflows."""

    master = 'master'
    develop = 'develop'
    release = 'release'
    hotfix = 'hotfix'


class Workflow(str, Enum):  # noqa: WPS600
    """Supported workflows."""

    git_flow = 'git_flow'
    m_flow = 'm_flow'
    free_flow = 'free_flow'

    def __str__(self):
        """Return the string representation of the workflow.

        Returns:
            The string representation of the workflow.
        """
        return self.value


class GitFlowConfig(BaseModel):
    """An object mapping branches for the git_flow workflow."""

    master_branch: str | Branches = Branches.master
    develop_branch: str | Branches = Branches.develop
    release_prefix: str | Branches = Branches.release
    hotfix_prefix: str | Branches = Branches.hotfix


class MFlowConfig(BaseModel):
    """An object mapping branches for the m_flow workflow."""

    master_branch: str | Branches = Branches.master
    release_prefix: str | Branches = Branches.release
    hotfix_prefix: str | Branches = Branches.hotfix
