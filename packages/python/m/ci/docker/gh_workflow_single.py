from textwrap import dedent
from typing import Any

from m.core import yaml
from pydantic import BaseModel

from .image import DockerImage
from .workflow_input import GithubWorkflowInput

TEMPLATE = """\
# AUTOGENERATED FILE - Do not update by hand!
# Edit {m_dir}/m.yaml then run
# `m blueprints` to update
name: m

on:
  workflow_call:
    inputs:
      m-tag:
        type: string
        description: The unique version to use for all the images
        required: true
      cache-from-pr:
        type: string
        description: The pull request number to attempt to use as cache.
        required: true{extra_inputs}

permissions: write-all

env:{global_env}

jobs:
  blueprints:
    runs-on: {default_runner}{container}
    steps:
      - name: checkout
        uses: actions/checkout@v4
      - name: install-m
        run: pip install jmlopez-m
      - name: m-blueprints
        id: m-blueprints
        run: |-
          m blueprints --skip-makefile --skip-workflow {m_dir}
      - name: archive
        uses: actions/upload-artifact@v3
        with:
          name: m-blueprints
          path: {ci_dir}
      - name: chmod
        run: chmod +x {ci_dir}/*.sh
      - {docker_login}
      {build_steps}
"""


class TemplateVars(BaseModel):
    """Template variables."""

    m_dir: str

    ci_dir: str

    default_runner: str

    container: str

    global_env: str

    docker_login: str

    build_steps: str

    extra_inputs: str


def _indent(text: str, num: int) -> str:
    spaces = '  ' * num
    return text.replace('\n', f'\n{spaces}', -1)


class Workflow(BaseModel):
    """Helper class to write the `m` workflow."""

    m_dir: str

    ci_dir: str

    global_env: dict[str, str] | None

    default_runner: str

    docker_registry: str

    extra_build_steps: list[dict[str, Any]] | None

    extra_inputs: dict[str, GithubWorkflowInput] | None

    container: dict[str, Any] | None

    images: list[DockerImage]

    def docker_login_str(self: 'Workflow') -> str:
        """Generate a github action str to login to docker.

        Returns:
            A string to add to the Github workflow.
        """
        login_obj = """\
            name: docker-login
            uses: docker/login-action@v3
            with:
              registry: ghcr.io
              username: ${{ github.actor }}
              password: ${{ secrets.GITHUB_TOKEN }}"""
        return _indent(dedent(login_obj), 4)

    def global_env_str(self: 'Workflow') -> str:
        """Generate a github action str with the global environment variables.

        Returns:
            A string to add to the Github workflow.
        """
        all_vars = {
            'GITHUB_TOKEN': '${{ secrets.GITHUB_TOKEN }}',
            'M_TAG': '${{ inputs.m-tag }}',
            'M_CACHE_FROM_PR': '${{ inputs.cache-from-pr }}',
            **(self.global_env or {}),
        }
        vars_str = '\n'.join([
            f'  {env_var}: {env_val}'
            for env_var, env_val in all_vars.items()
        ])
        return f'\n{vars_str}'

    def extra_inputs_str(self: 'Workflow') -> str:
        """Generate a github action str with the extra inputs.

        Returns:
            A string to add to the Github workflow.
        """
        if not self.extra_inputs:
            return ''
        lines: list[str] = []
        extras = {
            key: input_inst.model_dump()
            for key, input_inst in self.extra_inputs.items()
        }
        inputs_str = _indent(yaml.dumps(extras), 3)
        lines.append(f'\n      {inputs_str}')
        return '\n'.join(lines).rstrip()

    def container_str(self: 'Workflow') -> str:
        """Generate a string specifying a container to run on.

        Returns:
            A string to add to the Github workflow.
        """
        if not self.container:
            return ''
        lines: list[str] = ['\n    container:']
        content_str = _indent(yaml.dumps(self.container), 3)
        lines.append(f'      {content_str}')
        return '\n'.join(lines).rstrip()

    def build_steps_str(self: 'Workflow') -> str:
        """Generate a github action str for the build steps.

        Returns:
            A string to add to the Github workflow.
        """
        lines: list[str] = []
        for step in self.extra_build_steps or []:
            step_str = _indent(yaml.dumps(step)[:-1], 1)
            lines.append(f'- {step_str}')
        for img in self.images:
            cache_sh = f'{self.ci_dir}/_find-cache.sh'
            build_sh = f'{self.ci_dir}/{img.image_name}.build.sh'
            push_sh = f'{self.ci_dir}/_push-image.sh'
            image_steps = [
                f'- name: {img.image_name} - cache',
                f'  run: {cache_sh} {img.image_name}',
                f'- name: {img.image_name} - build',
                f'  run: {build_sh}',
                f'- name: {img.image_name} - push',
                f'  run: {push_sh} {img.image_name}',
            ]
            lines.extend(image_steps)
        return _indent('\n'.join(lines), 3)

    def __str__(self: 'Workflow') -> str:
        """Stringify the workflow file.

        Returns:
            The github workflow.
        """
        template_vars = TemplateVars(
            m_dir=self.m_dir,
            default_runner=self.default_runner,
            global_env=self.global_env_str(),
            ci_dir=self.ci_dir,
            docker_login=self.docker_login_str(),
            build_steps=self.build_steps_str(),
            extra_inputs=self.extra_inputs_str(),
            container=self.container_str(),
        )
        return TEMPLATE.format(**template_vars.model_dump())
