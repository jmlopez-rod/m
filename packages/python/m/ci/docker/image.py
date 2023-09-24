from m.core import Bad, Good, Res
from m.core.rw import read_file
from pydantic import BaseModel

from .docker_build import DockerBuild
from .env import MEnvDocker

BASH_SHEBANG = '#!/bin/bash'
SET_STRICT_BASH = 'set -euxo pipefail'


class DockerImage(BaseModel):
    """Information describing how to a docker image."""

    # String used to describe the step in the workflow.
    step_name: str

    # The name of the image - usually prefixed with the name of the repo.
    image_name: str

    # Name of the docker file to use for the build step.
    docker_file: str

    # Name of a target stage to build. Leave empty to build the whole file.
    target_stage: str | None = None

    # Arguments to pass to the docker build command, they will only be injected
    # if they appear within the docker file.
    build_args: dict[str, str] = {}

    # name of envvars to be treated as secrets.
    env_secrets: list[str] | None = None

    def format_build_args(
        self: 'DockerImage',
        m_env: MEnvDocker,
        arch: str,
        extras: dict[str, str] | None = None,
    ) -> Res[list[str]]:
        """Format the arguments to pass to the docker build command.

        Docker will only inject build args if they appear in the docker file.

        Args:
            m_env: The MEnvDocker instance with the environment variables.
            arch: The architecture to build for.
            extras: Extra build arguments.

        Returns:
            A list with the build arguments.
        """
        docker_file = f'{m_env.base_path}/{self.docker_file}'
        docker_file_res = read_file(docker_file)
        if isinstance(docker_file_res, Bad):
            return Bad(docker_file_res.value)
        docker_file_contents = docker_file_res.value
        all_args = {
            'M_TAG': m_env.m_tag,
            **(extras or {}),
            **self.build_args,
        }
        # Only add the arch if multi-arch is enabled.
        if m_env.multi_arch:
            all_args['ARCH'] = arch
        return Good([
            f'{key}={arg_value}'
            for key, arg_value in all_args.items()
            if f'ARG {key}' in docker_file_contents
        ])

    def format_env_secrets(self: 'DockerImage') -> list[str] | None:
        """Format the environment secrets to pass to the docker build command.

        Returns:
            A list of valid `secret` arguments.
        """
        env_sec = self.env_secrets or []
        return [f'id={env}' for env in env_sec] if env_sec else None

    def ci_build(self: 'DockerImage', m_env: MEnvDocker) -> Res[str]:
        """Generate a shell script to build an image in the CI pipelines.

        Args:
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            A shell snippet with a docker build command.
        """
        build_args = self.format_build_args(m_env, '"$ARCH"')
        if isinstance(build_args, Bad):
            return Bad(build_args.value)
        build_args.value.append('BUILDKIT_INLINE_CACHE=1')

        docker_file = f'{m_env.base_path}/{self.docker_file}'
        img_name = f'{m_env.registry}/{self.image_name}'
        build_cmd = DockerBuild(
            progress='plain',
            cache_from='staged-image:cache',
            secret=self.format_env_secrets(),
            tag=[
                'staged-image:latest',
                f'{img_name}:{m_env.m_tag}',
            ],
            build_arg=build_args.value,
            target=self.target_stage,
            file=docker_file,
        )
        script = [
            BASH_SHEBANG,
            'export DOCKER_BUILDKIT=1',
            SET_STRICT_BASH,
            '',
            str(build_cmd),
            '',
        ]
        return Good('\n'.join(script))

    def local_build(self: 'DockerImage', m_env: MEnvDocker) -> Res[str]:
        """Generate a shell script to build an image.

        Args:
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            A shell snippet with a docker build command.
        """
        build_args = self.format_build_args(m_env, 'local')
        if isinstance(build_args, Bad):
            return Bad(build_args.value)

        docker_file = f'{m_env.base_path}/{self.docker_file}'
        img_name = f'{m_env.registry}/{self.image_name}'
        build_cmd = DockerBuild(
            progress='plain',
            secret=self.format_env_secrets(),
            tag=[
                'staged-image:latest',
                f'{img_name}:{m_env.m_tag}',
            ],
            build_arg=build_args.value,
            target=self.target_stage,
            file=docker_file,
        )
        script = [
            BASH_SHEBANG,
            'export DOCKER_BUILDKIT=1',
            SET_STRICT_BASH,
            '',
            str(build_cmd),
            '',
        ]
        return Good('\n'.join(script))
