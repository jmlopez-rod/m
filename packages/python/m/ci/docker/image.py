from m.core import Bad, Good, Res
from m.core.rw import read_file
from pydantic import BaseModel

from .docker_build import DockerBuild
from .env import MEnvDocker
from .tags import docker_tags


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

    def img_name(self: 'DockerImage', m_env: MEnvDocker, arch: str = '') -> str:
        """Generate name of the image.

        Args:
            m_env: The MEnvDocker instance with the environment variables.
            arch: The architecture to build for.

        Returns:
            The full name of the image.
        """
        with_arch = f'{arch}-' if arch else ''
        return f'{m_env.registry}/{with_arch}{self.image_name}'

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
            'ARCH': arch,
            'M_TAG': m_env.m_tag,
            **(extras or {}),
            **self.build_args,
        }
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
        build_args = self.format_build_args(m_env, '"$ARCH"', {
            'BUILDKIT_INLINE_CACHE': '1',
        })
        if isinstance(build_args, Bad):
            return Bad(build_args.value)

        docker_file = f'{m_env.base_path}/{self.docker_file}'
        img_name = self.img_name(m_env)
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
            '#!/bin/bash',
            'export DOCKER_BUILDKIT=1',
            'set -euxo pipefail',
            '',
            str(build_cmd),
        ]
        return Good('\n'.join(script))

    def ci_cache(self: 'DockerImage', m_env: MEnvDocker) -> Res[str]:
        """Generate a shell script to obtain an image to use as cache.

        Args:
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            A shell snippet with commands to pull an image.
        """
        pr_num = m_env.pr_number or m_env.associated_pr_number
        pulls = ['pullCache "$1" master', 'echo "NO CACHE FOUND"']
        if pr_num:
            pulls.insert(0, f'pullCache "$1" "pr{pr_num}"')
        find_cache_implementation = ' || '.join(pulls)
        img_name = self.img_name(m_env)
        script = [
            '#!/bin/bash',
            'pullCache() {',
            '  if docker pull -q "$1:$2" 2> /dev/null; then',
            '    docker tag "$1:$2" "staged-image:cache"',
            '  else',
            '    return 1',
            '  fi',
            '}',
            'findCache() {',
            f'  {find_cache_implementation}',
            '}',
            'set -euxo pipefail',
            f'findCache {img_name}',
            '',
        ]
        return Good('\n'.join(script))

    def ci_push(self: 'DockerImage', m_env: MEnvDocker) -> Res[str]:
        """Generate a shell script to obtain an image to use as cache.

        Args:
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            A shell snippet with commands to pull an image.
        """
        img_name_arch = self.img_name(m_env, '"$ARCH"')
        script = [
            '#!/bin/bash',
            'set -euxo pipefail',
            f'docker tag staged-image:latest {img_name_arch}:{m_env.m_tag}',
            f'docker push {img_name_arch}:{m_env.m_tag}',
            '',
        ]
        return Good('\n'.join(script))

    def ci_manifest(
        self: 'DockerImage',
        m_env: MEnvDocker,
        architectures: dict[str, str | list[str]],
    ) -> dict[str, str]:
        """Generate a shell script to create and push a manifest.

        For instance, say we have the following images already pushed to the
        registry:

            - registry/amd64-some-image:mtag
            - registry/arm64-some-image:mtag

        The goal is to create a manifest so that we may access the image

            - registry/some-image:tag

        These manifests will point to the same image.

        Args:
            m_env: The MEnvDocker instance with the environment variables.
            architectures: The architectures to use.

        Returns:
            A shell snippet with commands to create and push a manifest.
        """
        img_name = self.img_name(m_env)
        all_tags = [m_env.m_tag, *docker_tags(m_env.m_tag)]
        existing_images = [
            ':'.join((self.img_name(m_env, arch), m_env.m_tag))
            for arch in architectures
        ]
        manifests: dict[str, str] = {}
        for tag in all_tags:
            final_img = f'{img_name}:{tag}'
            bundle = ' \\\n  '.join(existing_images)
            script = [
                '#!/bin/bash',
                'set -euxo pipefail',
                f'docker manifest create {final_img} \\',
                f'  {bundle}',
                f'docker manifest push {final_img}',
                '',
            ]
            manifests[f'{self.image_name}__{tag}'] = '\n'.join(script)
        return manifests


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
        img_name = self.img_name(m_env)
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
            '#!/bin/bash',
            'export DOCKER_BUILDKIT=1',
            'set -euxo pipefail',
            '',
            str(build_cmd),
        ]
        return Good('\n'.join(script))
