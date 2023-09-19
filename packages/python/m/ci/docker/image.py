from m.core import Bad, Good, Res
from m.core.rw import read_file
from pydantic import BaseModel

from .docker_build import DockerBuild
from .env import MEnvDocker


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
    build_args: dict[str, str] = {}

    # name of envvars to be treated as secrets.
    env_secrets: list[str] | None = None

    def img_name(self: 'DockerImage', m_env: MEnvDocker) -> str:
        """Generate name of the image.

        Returns:
            The full name of the image.
        """
        return f'{m_env.registry}/{self.image_name}'


    def local_build(self: 'DockerImage', m_env: MEnvDocker) -> Res[str]:
        """Generate a shell script to build an image.

        Returns:
            A shell snippet with a docker build command.
        """
        docker_file = f'{m_env.base_path}/{self.docker_file}'
        docker_file_res = read_file(docker_file)
        if isinstance(docker_file_res, Bad):
            return Bad(docker_file_res.value)
        docker_file_contents = docker_file_res.value
        all_args = {
            'ARCH': 'local',
            'M_TAG': m_env.m_tag,
            **self.build_args,
        }
        filtered_args = [
            f'{key}={value}'
            for key, value in all_args.items()
            if f'ARG {key}' in docker_file_contents
        ]

        img_name = self.img_name(m_env)
        env_sec = self.env_secrets or []
        secrets = [f'id={env}' for env in env_sec] if env_sec else None
        build_cmd = DockerBuild(
            progress='plain',
            secret=secrets,
            tag=[
                'staged-image:latest',
                f'{img_name}:{m_env.m_tag}',
            ],
            build_arg=filtered_args,
            target=self.target_stage,
            file=docker_file,
        )
        script = [
            '#!/bin/bash',
            'export DOCKER_BUILDKIT=1',
            'set -euxo pipefail',
            '',
            str(build_cmd),
        ]
        return Good('\n'.join(script))
