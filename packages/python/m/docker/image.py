from pydantic import BaseModel

from .docker_build import DockerBuild


class DockerImage(BaseModel):
    """Information describing how to a docker image."""

    # String used to describe the step in the workflow.
    step_name: str

    # The name of the image - usually prefixed with the name of the repo.
    image_name: str

    # Name of the docker file to use for the build step.
    docker_file: str

    # Name of a target stage to build. Leave empty to build the whole file.
    target_stage: str = ''

    # Arguments to pass to the docker build command, they will only be injected
    # if they appear within the docker file.
    arguments: dict[str, str] = {}

    def local_build(self: 'DockerImage') -> str:
        """Generate a shell script to build an image.

        Returns:
            A shell snippet with a docker build command.
        """
        build_cmd = DockerBuild(tag=['boo'])
        script = [
            '#!/bin/bash',
            '',
            str(build_cmd),
        ]
        return '\n'.join(script)
