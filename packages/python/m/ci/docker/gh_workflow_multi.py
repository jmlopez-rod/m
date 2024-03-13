from .gh_workflow_single import TemplateVars as DefaultTemplateVars
from .gh_workflow_single import Workflow as DefaultWorkflow
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
    runs-on: {default_runner}
    outputs:
      image-names: ${{{{ steps.m-blueprints.outputs.image-names }}}}
      image-tags: ${{{{ steps.m-blueprints.outputs.image-tags }}}}
    steps:
      - name: checkout
        uses: actions/checkout@v4
      - name: install-m
        run: pip install jmlopez-m
      - name: m-blueprints
        id: m-blueprints
        run: |-
          m blueprints --skip-makefile --skip-workflow {m_dir}
          {{
            echo "image-names=$(< {ci_dir}/_image-names.json)"
            echo "image-tags=$(< {ci_dir}/_image-tags.json)"
          }} >> $GITHUB_OUTPUT
      - name: archive
        uses: actions/upload-artifact@v3
        with:
          name: m-blueprints
          path: {ci_dir}

  build:
    needs: blueprints
    strategy:
      fail-fast: false
      matrix:
        include:{build_architectures}
    runs-on: ${{{{ matrix.os }}}}
    env:
      ARCH: ${{{{ matrix.arch }}}}
    steps:
      - name: checkout
        uses: actions/checkout@v4
      - name: restore-m-blueprints
        uses: actions/download-artifact@v3
        with:
          name: m-blueprints
          path: {ci_dir}
      - name: chmod
        run: chmod +x {ci_dir}/*.sh
      - {docker_login}
      {build_steps}

  manifest:
    runs-on: {default_runner}
    needs: [blueprints, build]
    strategy:{manifest_strategy_options}
      matrix:
        image-name: ${{{{ fromJSON(needs.blueprints.outputs.image-names) }}}}
        image-tag: ${{{{ fromJSON(needs.blueprints.outputs.image-tags) }}}}
    steps:
      - {docker_login}
      - name: create
        run: {create_manifest}
      - name: push
        run: {push_manifest}
"""


class TemplateVars(DefaultTemplateVars):
    """Template variables."""

    build_architectures: str

    create_manifest: str

    push_manifest: str

    manifest_strategy_options: str


def _indent(text: str, num: int) -> str:
    spaces = '  ' * num
    return text.replace('\n', f'\n{spaces}', -1)


class Workflow(DefaultWorkflow):
    """Helper class to write the `m` workflow."""

    architectures: dict[str, str | list[str]]

    max_parallel_manifests: int | None

    def build_architectures(self: 'Workflow') -> str:
        """Generate a github action str with the build architectures.

        Returns:
            A string to add to the Github workflow.
        """
        arch_strs = '\n'.join([
            f'- arch: {arch}\n  os: {os}'
            for arch, os in self.architectures.items()
        ])
        return _indent(f'\n{arch_strs}', 5)

    def create_manifest_str(self: 'Workflow') -> str:
        """Generate the script to create the manifest.

        Returns:
            The manifest create script.
        """
        cmd = 'docker manifest create'
        registry = self.docker_registry
        image = '${{ matrix.image-name }}'
        tag = '${{ matrix.image-tag }}'
        m_tag = '${{ inputs.m-tag }}'
        lines = [f'{cmd} {registry}/{image}:{tag}']
        for arch in self.architectures:
            lines.append(f'  {registry}/{arch}-{image}:{m_tag}')
        # wants it be a raw string but i need a new line after `\`
        full_cmd = ' \\\n'.join(lines)   # noqa: WPS342
        return _indent(f'|-\n{full_cmd}', 5)

    def push_manifest_str(self: 'Workflow') -> str:
        """Generate the script to run to push the manifest.

        Returns:
            The command to push.
        """
        cmd = 'docker manifest push'
        registry = self.docker_registry
        image = '${{ matrix.image-name }}'
        tag = '${{ matrix.image-tag }}'
        full_cmd = f'|-\n{cmd} {registry}/{image}:{tag}'
        return _indent(full_cmd, 5)

    def manifest_strategy_options_str(self: 'Workflow') -> str:
        """Generate the strategy options for the manifest job.

        Returns:
            The strategy options.
        """
        options = ''
        if self.max_parallel_manifests:
            options = f'\n      max-parallel: {self.max_parallel_manifests}'
        return options

    def __str__(self: 'Workflow') -> str:
        """Stringify the workflow file.

        Returns:
            The github workflow.
        """
        template_vars = TemplateVars(
            m_dir=self.m_dir,
            default_runner=self.default_runner,
            global_env=self.global_env_str(),
            extra_inputs=self.extra_inputs_str(),
            ci_dir=self.ci_dir,
            build_architectures=self.build_architectures(),
            docker_login=self.docker_login_str(),
            build_steps=self.build_steps_str(),
            create_manifest=self.create_manifest_str(),
            push_manifest=self.push_manifest_str(),
            manifest_strategy_options=self.manifest_strategy_options_str(),
        )
        return TEMPLATE.format(**template_vars.model_dump())
