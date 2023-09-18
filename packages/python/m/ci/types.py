from enum import StrEnum

from pydantic import BaseModel


class Branches(StrEnum):
    """Default branches to use for the supported workflows."""

    master = 'master'
    develop = 'develop'
    release = 'release'
    hotfix = 'hotfix'


class Workflow(StrEnum):
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


class DockerImage(BaseModel):
    """Information describing how to a docker image."""

    # Name to describe the image
    name: str

    # Name of the docker file to use for the build step.
    docker_file: str

    # Name of a target stage to build. Leave empty to build the whole file.
    target_stage: str = ''

    # Arguments to pass to the docker build command, they will only be injected
    # if they appear within the docker file.
    arguments: dict[str, str] = {}


class DockerImages(BaseModel):
    """Contains information about the docker images to build."""

    # A map of the architectures to build. It maps say `amd64` to a Github
    # runner that will build the image for that architecture.
    #   amd64: Ubuntu 20.04
    architectures: dict[str, str]

    # Base path used to locate docker files. Defaults to `.` (root of project)
    # but may be changed a specific directory.
    base_path: str = '.'

    # list of images to build
    images: list[DockerImage]
