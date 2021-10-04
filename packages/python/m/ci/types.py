from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from ..core import Good, Issue, OneOf, issue
from ..core.io import JsonStr


class Branches(Enum):
    """Default branches to use for the supported workflows."""

    master = 'master'
    develop = 'develop'
    release = 'release'
    hotfix = 'hotfix'

    def __str__(self) -> str:
        """Stringify the `Branches` enum.

        Returns:
            The value of the enum.
        """
        return str(self.value)


class Workflow(Enum):
    """Supported workflows."""

    git_flow = 'git_flow'
    m_flow = 'm_flow'
    free_flow = 'free_flow'

    def __str__(self) -> str:
        """Stringify the `Workflow` enum.

        Returns:
            The value of the enum.
        """
        return str(self.value)


@dataclass
class GitFlowConfig(JsonStr):
    """An object mapping branches for the git_flow workflow."""

    master_branch: str = str(Branches.master)
    develop_branch: str = str(Branches.develop)
    release_prefix: str = str(Branches.release)
    hotfix_prefix: str = str(Branches.hotfix)


@dataclass
class MFlowConfig(JsonStr):
    """An object mapping branches for the m_flow workflow."""

    master_branch: str = str(Branches.master)
    release_prefix: str = str(Branches.release)
    hotfix_prefix: str = str(Branches.hotfix)


def read_workflow(raw_name: str) -> OneOf[Issue, Workflow]:
    """Parse the workflow field.

    Args:
        raw_name:
            The name of the workflow in the configuration. Dashes are allowed.
            For instance `git-flow`, 'm-flow`, but an underscore will work too.

    Returns:
        A `OneOf` containing a `Workflow` enum or and `Issue`.
    """
    name = raw_name.lower().replace('-', '_')
    try:
        return Good(Workflow[name])
    except Exception as ex:
        return issue('invalid workflow', cause=ex)


def read_git_flow(prop_val: Mapping[str, Any]) -> OneOf[Issue, GitFlowConfig]:
    """Parse the gitFlow field.

    Args:
        prop_val: The dictionary value in the gitFlow field.

    Returns:
        A `OneOf` containing a GitFlowConfig instance.
    """
    config = GitFlowConfig(
        master_branch=prop_val.get('masterBranch', str(Branches.master)),
        develop_branch=prop_val.get('developBranch', str(Branches.develop)),
        release_prefix=prop_val.get('releasePrefix', str(Branches.release)),
        hotfix_prefix=prop_val.get('hotfixPrefix', str(Branches.hotfix)),
    )
    return Good(config)


def read_m_flow(prop_val: Mapping[str, Any]) -> OneOf[Issue, MFlowConfig]:
    """Parse the mFlow field.

    Args:
        prop_val: The dictionary value in the mFlow field.

    Returns:
        A `OneOf` containing a MFlowConfig instance.
    """
    config = MFlowConfig(
        master_branch=prop_val.get('masterBranch', str(Branches.master)),
        release_prefix=prop_val.get('releasePrefix', str(Branches.release)),
        hotfix_prefix=prop_val.get('hotfixPrefix', str(Branches.hotfix)),
    )
    return Good(config)
